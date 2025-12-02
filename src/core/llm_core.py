from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, ValidationError

from ..assets import AssetsInfo

import logging
logger = logging.getLogger('TestGen.llm_core')


class LLMExecutionError(Exception):
    """LLM执行过程中的错误，可以继续处理"""
    pass


class SystemError(Exception):
    """系统级错误，需要停止任务"""
    pass

async def run_llm_loop(
        prompt_template: str,
        output_pydantic: BaseModel,
        format_args: Dict[str, Any],
        tool_list: List[BaseTool] = [],
        max_tool_iterations: Optional[int] = 20
    ) -> Dict[str, Any]:
    """
    单轮LLM交互，支持工具调用循环。
    工具调用循环会持续直到LLM返回最终结果（status为completed或failed）。
    
    Args:
        prompt_template: 提示词模板
        output_pydantic: 输出格式的Pydantic模型，必须包含status字段（completed/failed）
        format_args: 用于格式化提示词的参数字典
        tool_list: 可用的工具列表
        max_tool_iterations: 最大工具调用迭代次数
        
    Returns:
        解析后的响应字典
    """
    llm = ChatOpenAI(
        model=AssetsInfo.openai_model,
        api_key=AssetsInfo.openai_api_key,
        base_url=AssetsInfo.openai_api_url,
    )

    tool_dict = {tool.name: tool for tool in tool_list}
    if tool_list:
        llm = llm.bind_tools(tool_list)

    parser = JsonOutputParser(pydantic_object=output_pydantic)

    if 'format_information' not in format_args:
        format_args['format_information'] = parser.get_format_instructions()

    messages = [HumanMessage(content=prompt_template.format(**format_args))]
    iteration = 0
    response = None

    while iteration < max_tool_iterations:
        iteration += 1
        logger.debug(f'tool iteration: {iteration}')
        
        try:
            response = await llm.ainvoke(messages)
        except Exception as e:
            # API调用失败是系统错误
            logger.error(f'LLM API调用失败: {e}')
            raise SystemError(f'LLM API调用失败: {e}') from e
        
        # 处理工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call.get('args', {})
                try:
                    tool_result = tool_dict[tool_name].invoke(tool_args)
                    messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call.get('id', '')))
                except Exception as e:
                    # 工具调用错误是LLM执行错误
                    logger.warning(f'工具调用失败 ({tool_name}): {e}')
                    # 将错误信息传递给LLM，让它知道工具调用失败
                    error_msg = f"工具 {tool_name} 调用失败: {str(e)}"
                    messages.append(ToolMessage(content=error_msg, tool_call_id=tool_call.get('id', '')))
            continue
        
        # 没有工具调用，解析最终响应
        try:
            parsed_response = parser.parse(response.content)
        except (ValueError, ValidationError, Exception) as e:
            # JSON解析错误是LLM执行错误
            logger.warning(f'JSON解析失败: {e}, 响应内容: {response.content[:200]}...')
            raise LLMExecutionError(f'JSON解析失败: {e}') from e
        
        status = parsed_response.get('status', '---')
        
        if status == '---':
            logger.warning(f'status is not in the response: {parsed_response}')
            raise LLMExecutionError(f'Response missing status field: {parsed_response}')
        
        if status in ['completed', 'failed']:
            return parsed_response
        else:
            logger.warning(f'unknown status: {status}')
            raise LLMExecutionError(f'Invalid status: {status}')

    # 达到最大迭代次数，尝试解析最后一次响应
    try:
        parsed_response = parser.parse(response.content)
        return parsed_response
    except Exception as e:
        logger.warning(f'达到最大迭代次数，JSON解析失败: {e}')
        raise LLMExecutionError(f'达到最大迭代次数且JSON解析失败: {e}') from e
