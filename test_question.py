import asyncio
from src.TestGen.expert import get_answer
from src.core.llm_core import run_llm_loop
from src.TestGen.prompt import AnswerOutput

import logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("TestGen")
logger.setLevel(logging.DEBUG)


# 不使用RAG tools的提示词
NO_RAG_PROMPT = """你是一个专业的软件测试专家，擅长回答关于软件测试、Property-Based Testing、Metamorphic Testing等相关问题。

你的任务是根据用户的问题，基于你的专业知识，提供准确、详细的回答。

**重要说明：**
- 你只能使用你自身的知识来回答问题，无法访问任何外部数据库或文档
- 请基于你的专业知识和对软件测试领域的理解来回答
- 如果某些具体细节你不太确定，可以说明这是基于一般知识的回答

**回答要求：**
- 回答要准确、详细、有条理
- 基于你的专业知识，尽可能提供全面的回答
- 回答要清晰易懂，适合不同技术水平的读者
- 如果涉及具体的技术细节或案例，可以说明这是基于一般知识的理解

**用户问题：**
{query}

**输出格式说明：**
{format_information}
"""


async def get_answer_without_rag(query: str) -> str:
    """
    不使用RAG tools，仅基于LLM自身知识回答问题
    
    参数:
    - query: 用户的问题
    
    返回:
    - 完整的回答字符串
    """
    result = await run_llm_loop(
        prompt_template=NO_RAG_PROMPT,
        output_pydantic=AnswerOutput,
        format_args={"query": query},
        tool_list=[],  # 不提供任何工具
        max_tool_iterations=1  # 不需要工具调用，只需要一次响应
    )
    
    if result.get('status') == 'failed':
        error_msg = result.get('message', '未知错误')
        raise RuntimeError(f"LLM处理失败: {error_msg}")
    
    return result.get('answer', '')


async def main():
    """对比测试：RAG vs 无RAG"""
    test_queries = [
        "测试的本质是什么？",
        "Oracle问题在软件测试中的核心地位是什么？Metamorphic Testing如何从根本上解决Oracle问题？",
        "Property-Based Testing和传统测试方法（如等价类划分、边界值分析）在测试理念和实践上有哪些根本性差异？",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"问题 {i}/{len(test_queries)}: {query}")
        print('='*80)
        
        # 测试1: 使用RAG tools
        print("\n【使用RAG工具的回答】")
        print("-" * 80)
        try:
            answer_with_rag = await get_answer(query)
            print(f"{answer_with_rag}")
        except Exception as e:
            print(f"错误: {e}")
        
        print("\n" + "-" * 80)
        
        # 测试2: 不使用RAG tools
        print("\n【不使用RAG工具的回答（仅基于LLM自身知识）】")
        print("-" * 80)
        try:
            answer_without_rag = await get_answer_without_rag(query)
            print(f"{answer_without_rag}")
        except Exception as e:
            print(f"错误: {e}")
        
        print('='*80)


if __name__ == "__main__":
    asyncio.run(main())
