from langchain_core.tools import tool
from langchain_core.documents import Document
from typing import List
import logging

logger = logging.getLogger("TestGen.researcher.tools")

# 全局状态
_global_state = {
    "current_content": "",
    "content_position": 0,
    "next_init_content": "",
    "leave_message": ""
}

# 全局向量数据库实例（由researcher.py初始化）
_vectorstore = None

def set_vectorstore(vectorstore):
    """设置全局向量数据库实例"""
    global _vectorstore
    _vectorstore = vectorstore

def get_global_state():
    """获取全局状态"""
    return _global_state

def reset_global_state():
    """重置全局状态"""
    global _global_state
    _global_state = {
        "current_content": "",
        "content_position": 0,
        "next_init_content": "",
        "leave_message": ""
    }

@tool
def write_notes(book_name: str, chapter_name: str, abstract: str, content: str) -> str:
    """
    将重要章节保存到向量数据库中，用于后续的RAG检索。
    
    重要：请严格按照语义边界调用此函数，不要强制截断内容。
    
    参数：
    - book_name: 文献名称（如 "Hypothesis"）
    - chapter_name: 章节标题，不超过50个字符，必须简洁明确地概括章节主题，避免重复或过于相似的标题
    - abstract: 章节摘要，不超过200个字符，必须准确概括核心观点
    - content: 文献原文内容，**严格不超过2000个字符**，必须在语义边界处截断（完整句子、段落结束处）
    
    所有参数都不能为空，且必须严格符合长度限制。如果content超过2000字符，函数会报错。
    """
    if not book_name or not chapter_name or not abstract or not content:
        raise ValueError("所有字段都不能为空")
    
    if len(chapter_name) > 50:
        raise ValueError(f"chapter_name超过50个字符: {len(chapter_name)}")
    if len(abstract) > 200:
        raise ValueError(f"abstract超过200个字符: {len(abstract)}")
    if len(content) > 2000:
        raise ValueError(f"content超过2000个字符: {len(content)}")
    
    if _vectorstore is None:
        raise RuntimeError("向量数据库未初始化，任务失败并退出")
    
    # 创建Document对象
    # 注意：这里创建的Document会直接添加到向量数据库，不会重新分块
    # LLM已经完成了语义分块，每个write_notes调用对应一个chunk
    full_content = f"章节: {chapter_name}\n摘要: {abstract}\n内容: {content}"
    doc = Document(
        page_content=full_content,
        metadata={
            "book_name": book_name,
            "chapter_name": chapter_name,
            "abstract": abstract
        }
    )
    
    # 直接添加到向量数据库，不会重新分块
    # add_documents方法会将Document原样添加，不会调用任何分块逻辑
    _vectorstore.add_documents([doc])
    
    logger.info(f"已写入笔记: {book_name} - {chapter_name}")
    return f"成功写入笔记: {book_name} - {chapter_name}"

@tool
def discard_slot(notes: str) -> str:
    """
    丢弃当前内容，不保存到数据库。
    
    参数：
    - notes: 要丢弃的内容说明（可选，用于记录原因）
    
    使用场景：当当前内容与核心概念无关，或质量不足以保存时调用。
    调用此函数后，当前内容不会被写入数据库。
    """
    return "已丢弃，未记录到数据库"

@tool
def get_more_raw_content() -> str:
    """
    从当前文献中获取更多原始内容，每次返回2000个字符。
    
    返回值：返回下一段2000字符的内容，如果已读完则返回空字符串。
    
    使用场景：当当前内容不足以理解某个概念，需要更多上下文时调用。
    可以多次调用以获取连续的内容片段。
    """
    state = get_global_state()
    current_content = state["current_content"]
    position = state["content_position"]
    
    if position >= len(current_content):
        return ""
    
    end_position = min(position + 2000, len(current_content))
    content = current_content[position:end_position]
    state["content_position"] = end_position
    
    return content

@tool
def set_init_content(content: str) -> str:
    """
    设置下一轮处理的初始内容。
    
    参数：
    - content: 下一轮要处理的文本内容
    
    使用场景：完成当前轮处理后，将剩余的或需要继续处理的内容通过此函数保存。
    下一轮处理时会自动使用这里设置的内容作为输入。
    """
    state = get_global_state()
    state["next_init_content"] = content
    return f"已设置下一轮初始内容，长度: {len(content)}"

@tool
def leave_message(message: str) -> str:
    """
    为下一轮处理留下备注或提示信息。
    
    参数：
    - message: 备注信息，建议简短（不超过100字符），说明需要注意的事项
    
    使用场景：当需要提醒下一轮处理时注意某些要点时调用。
    备注会自动添加到下一轮的提示词中，帮助保持上下文连续性。
    """
    state = get_global_state()
    state["leave_message"] = message
    return f"已记录备注: {message}"
