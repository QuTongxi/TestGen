from pathlib import Path
from typing import Optional
from langchain_core.tools import tool

from ..core.llm_core import run_llm_loop
from ..core.retriver import DocsRetriever
from ..assets import AssetsInfo
from .prompt import EXPERT_PROMPT, AnswerOutput


# 全局retriever实例，避免重复初始化
_retriever: Optional[DocsRetriever] = None


def _get_retriever() -> DocsRetriever:
    """获取或初始化retriever实例"""
    global _retriever
    if _retriever is None:
        _retriever = DocsRetriever(
            docs_path=AssetsInfo.pdfs_path,
            vector_path=AssetsInfo.pdfs_vector_path,
            chunk_size=500,
            chunk_overlap=100
        )
        if not _retriever.load_vectorstore():
            raise RuntimeError(f"无法加载向量数据库: {AssetsInfo.pdfs_vector_path}")
    return _retriever


@tool
def read_all_chapters() -> str:
    """
    从chapters.txt文件中读取所有章节名称，用于后续的RAG检索。
    
    返回所有章节名称的列表，每行一个章节名称。
    """
    chapters_file = Path(__file__).parent.parent.parent / "doc" / "pdfs" / "chapters.txt"
    if not chapters_file.exists():
        return f"错误: 章节文件不存在: {chapters_file}"
    
    with open(chapters_file, 'r', encoding='utf-8') as f:
        chapters = [line.strip() for line in f if line.strip()]
    
    return f"共有 {len(chapters)} 个章节:\n" + "\n".join(chapters)


@tool
def search_RAG(query: str, k: int = 5) -> str:
    """
    根据查询词，从向量数据库中检索相关章节，返回前k个最相关的章节内容。
    
    参数:
    - query: 查询词，用于检索相关章节
    - k: 返回的章节数量，默认为5
    
    返回检索到的章节内容，包括章节名称、摘要和内容。
    """
    try:
        retriever = _get_retriever()
        results = retriever.search(query, k=k, search_type="mmr")
        
        if not results:
            return "未找到相关章节。"
        
        output_lines = [f"找到 {len(results)} 个相关章节:\n"]
        for i, doc in enumerate(results, 1):
            metadata = doc.metadata
            chapter_name = metadata.get('chapter_name', 'Unknown')
            abstract = metadata.get('abstract', '')
            content = doc.page_content.strip()
            
            output_lines.append(f"\n【章节 {i}】{chapter_name}")
            if abstract:
                output_lines.append(f"摘要: {abstract}")
            output_lines.append(f"内容: {content[:500]}..." if len(content) > 500 else f"内容: {content}")
        
        return "\n".join(output_lines)
    except Exception as e:
        return f"检索失败: {str(e)}"


async def get_answer(query: str) -> str:
    """
    调用LLM，让LLM分析用户问题，调用工具获取数据库知识，并结合自身知识回答用户的问题。
    
    参数:
    - query: 用户的问题
    
    返回:
    - 完整的回答字符串
    """
    tools = [read_all_chapters, search_RAG]
    
    result = await run_llm_loop(
        prompt_template=EXPERT_PROMPT,
        output_pydantic=AnswerOutput,
        format_args={"query": query},
        tool_list=tools,
        max_tool_iterations=20
    )
    
    if result.get('status') == 'failed':
        error_msg = result.get('message', '未知错误')
        raise RuntimeError(f"LLM处理失败: {error_msg}")
    
    return result.get('answer', '')