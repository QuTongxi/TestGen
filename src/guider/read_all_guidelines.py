import asyncio
import json
from pathlib import Path
from typing import List, Dict, Literal, Any, Optional

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool, BaseTool
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, ValidationError

from ..assets import AssetsInfo
from ..core.llm_core import LLMExecutionError, SystemError

import logging

# 读 D:\workspace\TestGen\src\assets.py 并且将 guide 文件路径等其他路径配置放到assets.py中

logger = logging.getLogger("TestGen.guider") # 注意使用这个 logger 来记录日志，不要添加其他logger设置有关内容，我会在其他脚本中设置

# 注意提醒 LLM 做总结，不要随便自我发挥，让LLM调用工具，如果文献内容格式不对或者有笔误，让LLM可以修改，但是必须是完全确定此处错误且确保自己改的是对的
PROMPT = """
你的任务：
针对我提供的整篇文章，你需要依据原文内容完成“拆分 + 概括”的工作。
具体来说：你要将输入的原始文本流分解成多个小块，每个小块都由“当前窗口起点”到“窗口内某一句结尾”为止，形成一个连续的段落，并为该段撰写摘要。完成每个小块后，调用工具将该段内容记录下来，再继续处理剩余内容，直到全文被分块完毕。


整体要求：
1. 把文章拆分为 2000 字符以内的语义块（实际词数可能只有小几百）；如果收到 “content too long” 等提示，说明你你应该将目前看到的内容分成至少2块。
2. 记录内容必须严格使用原文，不得改写、删除或新增文本。
3. 【关键】当\"FAILED: 阅读窗口超过2000字符\"出现，说明当前chunk内容可能过多，必须在摘要加入 (part 1 / part 2 …) 表示关联，然后强制在中间某句话结尾处分块。
4. 仅有当前这一次输入，后续请你自主反复调用工具直至全文处理完毕。
5. 如果多次得到\"FAILED: 文中不存在\"的工具结果，必须确保你提供的last_sentence是原文内容，在多次尝试失败后可以尝试只将句子最后几个词汇作为last_sentence再次尝试。
6. 你有能力完成这个任务，如果多次出现tool执行失败的返回值，务必改变你传入的参数！
7. 【关键】你提供的last_sentence要么是一个完整句子，要么是一个完整句子最后的几个单词或者短语！
8. 【关键】一般来说，last_sentence的最后一个字符应该是标点符号，\"\\n\"，或者特殊符号，不恰当的分块会导致下一块的开头出现意义不明的内容，导致整个工作彻底失败！

下面是需要处理的原始内容：
{content}

请严格按照如下JSON格式输出：
{format_information}
"""

NOTES_FILE = Path(AssetsInfo.guidelines_json_path)
NOTES_STORE: List[Dict[str, str]] = []
NOTES_DIRTY = False

CURRENT_DOC_NAME: str = ""
CURRENT_DOC_CONTENT: str = ""
WINDOW_BUFFER: str = ""
WINDOW_START: int = 0
WINDOW_END: int = 0


def _load_notes() -> None:
    if NOTES_FILE.exists():
        data = json.loads(NOTES_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            NOTES_STORE.extend(item for item in data if isinstance(item, dict))


def _save_notes(force: bool = False) -> None:
    global NOTES_DIRTY
    if not (force or NOTES_DIRTY):
        return
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    NOTES_FILE.write_text(json.dumps(NOTES_STORE, ensure_ascii=False, indent=2), encoding="utf-8")
    NOTES_DIRTY = False


_load_notes()


class NotesLLMOutput(BaseModel):
    status: Literal['completed', 'failed', 'continue']
    message: str = Field(..., max_length=200, description="Brief description of current status or result")


async def run_llm_loop(
    prompt_template: str,
    output_pydantic: BaseModel,
    format_args: Dict[str, Any],
    tool_list: List[BaseTool] = [],
    max_tool_iterations: Optional[int] = None,
) -> Dict[str, Any]:
    """
    run_llm_loop 的本地拷贝，用于在本模块内修改。
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

    base_args = dict(format_args)
    if 'format_information' not in base_args:
        base_args['format_information'] = parser.get_format_instructions()

    iteration = 0
    conversation_history: List[AIMessage | ToolMessage | HumanMessage] = []

    while True:
        iteration += 1
        if max_tool_iterations and iteration > max_tool_iterations:
            raise LLMExecutionError("超过最大允许迭代次数，可能存在无限循环")
        logger.debug(f'iteration: {iteration}')

        current_args = dict(base_args)
        current_args['content'] = _current_window_content()
        messages = conversation_history + [HumanMessage(content=prompt_template.format(**current_args))]

        response = await llm.ainvoke(messages)

        while hasattr(response, 'tool_calls') and response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call.get('args', {})

                tool_result = tool_dict[tool_name].invoke(tool_args)
                result = str(tool_result)
                logger.debug(f'tool {tool_name} result: {result}')                   

                messages.append(ToolMessage(content=result, tool_call_id=tool_call.get('id', '')))

                response = await llm.ainvoke(messages)

        parsed_response = parser.parse(response.content)
        status = parsed_response.get('status', 'unknown')
        output = parsed_response.get('message', ' ')
        logger.info(f'LLM output: {output}')

        if status == 'unknown':
            raise "status is not in the response"
        elif status == 'completed':
            return parsed_response
        elif status == 'failed':
            raise "LLM failed"
        elif status == 'continue':
            conversation_history.append(AIMessage(content=output))
            continue

        raise "Invalid status"


def _load_more_impl() -> str:

    global WINDOW_END
    if not CURRENT_DOC_CONTENT:
        return "FAILED: 未初始化阅读窗口"

    if WINDOW_END >= len(CURRENT_DOC_CONTENT):
        return "WARNING: 文档已读完"

    next_end = min(WINDOW_END + 400, len(CURRENT_DOC_CONTENT))
    new_segment = CURRENT_DOC_CONTENT[WINDOW_END:next_end]

    if len(WINDOW_BUFFER) + len(new_segment) > 2000:
        return "FAILED: 阅读窗口超过2000字符，请先调用 build_chunk() 处理部分内容"

    _append_to_window(new_segment)
    WINDOW_END = next_end
    return f"SUCCESS: {new_segment}"


@tool
def load_more() -> str:
    """
    Append up to 400 additional characters from the current document into the sliding window.
    - Returns "WARNING" when the document has been fully read.
    - Returns "FAILED" if adding the characters would exceed the 2000-character window limit (caller should commit part of the window first).
    """
    return _load_more_impl()

@tool
def build_chunk(abstract: str, last_sentence: str) -> str:
    """
    Commit a chunk of text from the start of the current window up to the provided last sentence.
    - Saves the chunk (with abstract) into NOTES_STORE and flushes it to disk.
    - Returns "FAILED" for invalid parameters (e.g., missing sentence, chunk too long).
    """
    if not CURRENT_DOC_CONTENT:
        return "FAILED: 未初始化阅读窗口"

    abstract = abstract.strip()
    last_sentence = last_sentence.strip()

    if not last_sentence:
        return "FAILED: last_sentence 不能为空"

    pos = WINDOW_BUFFER.find(last_sentence)
    if pos == -1:
        return f"FAILED: 文中不存在{last_sentence}"

    chunk_end = pos + len(last_sentence)
    chunk = WINDOW_BUFFER[:chunk_end]

    if not chunk.strip():
        return "FAILED: 当前窗口没有可记录内容"


    NOTES_STORE.append(
        {
            "book_name": CURRENT_DOC_NAME,
            "abstract": abstract or "（暂无摘要）",
            "content": chunk,
        }
    )
    global NOTES_DIRTY
    NOTES_DIRTY = True
    _save_notes(force=True)

    _consume_window(chunk_end)
    return "SUCCESS: chunk 已记录"

@tool
def get_all_content() -> str:
    """
    Get all the content from the current window.
    """
    return _current_window_content()


def _collect_sources(arg: str) -> List[Dict[str, str]]:
    arg = arg.strip()
    if arg:
        return [{"book_name": "manual_input", "content": arg}]

    doc_dir = Path(AssetsInfo.good_guide_path)
    files = sorted(
        [p for p in doc_dir.glob("*.md")],
        key=lambda p: p.name.lower(),
    )
    return [
        {"book_name": file.stem, "content": file.read_text(encoding="utf-8")}
        for file in files
    ]


def _set_current_document(book_name: str, content: str):
    global CURRENT_DOC_NAME, CURRENT_DOC_CONTENT, WINDOW_BUFFER, WINDOW_START, WINDOW_END
    CURRENT_DOC_NAME = book_name
    CURRENT_DOC_CONTENT = content
    WINDOW_BUFFER = ""
    WINDOW_START = 0
    WINDOW_END = 0


def _append_to_window(chunk: str):
    global WINDOW_BUFFER
    WINDOW_BUFFER += chunk


def _consume_window(count: int):
    global WINDOW_BUFFER, WINDOW_START
    WINDOW_BUFFER = WINDOW_BUFFER[count:]
    WINDOW_START += count


def _current_window_content() -> str:
    return WINDOW_BUFFER


def _group_notes_by_book() -> Dict[str, List[Dict[str, str]]]:
    mapping: Dict[str, List[Dict[str, str]]] = {}
    for note in NOTES_STORE:
        mapping.setdefault(note.get("book_name", ""), []).append(note)
    return mapping


async def _run_pipeline(sources: List[Dict[str, str]]) -> int:
    existing_notes = _group_notes_by_book()
    processed = 0
    for source in sources:
        book_name = source["book_name"]
        book_name_1 = book_name.replace("_", " ")
        book_name_2 = book_name_1.replace("-", " ")

        if (
            book_name in existing_notes
            or book_name_1 in existing_notes
            or book_name_2 in existing_notes
        ):
            logger.info("跳过已处理文件: %s", book_name)
            continue

        logger.info("Processing guideline: %s", book_name)
        _set_current_document(book_name, source["content"])
        initial_status = _load_more_impl()
        logger.debug(f"初始加载状态: {initial_status}")
        await run_llm_loop(
            prompt_template=PROMPT,
            output_pydantic=NotesLLMOutput,
            format_args={"content": source["content"]},
            tool_list=[load_more, build_chunk, get_all_content],
            max_tool_iterations=10,
        )
        _save_notes(force=True)
        existing_notes = _group_notes_by_book()
        processed += 1
    return processed


# 读取所有指南，让LLM整理出 book_name: str, abstract: str, content: str，把这些信息存到文件中去。
# 你可以参考 D:\workspace\TestGen\src\core\llm_core.py 中的实现，
# 这是个简单的小功能，也只有一个 tool 可以用，但是注意每一轮可能会需要多次调用这个 tool
# 理论上iter至多为1，你可以简化这部分，对于debug消息，使用logger.debug()，且只需debug出来调用的tool的名称，无需其他内容
# 对于 info 消息，不要输出过多内容，无需输出类似 -*80 或者 =*80 这种分割线，我在其他脚本设置了输出格式
# 在运行结束之前，记得把全局变量保存成json
def read_guidelines(content: str):
    sources = _collect_sources(content)
    if not sources:
        return "未找到可处理的指南内容"

    processed = asyncio.run(_run_pipeline(sources))
    _save_notes(force=True)
