"""
在这里加入researcher的整体逻辑，注意有关的路径配置请写入文件assets.py中。
在这一阶段测试D:\\workspace\\repo\\doc\\pdfs\\Hypothesis.pdf这一个文件的表现即可，等我确定执行无误之后再做后续。
用于判断应该存入哪些内容的LLM通过调用API来实现，embeddding模型则是在本地，通过cuda启动。
"""
import os
import asyncio
import logging
from typing import List
from pydantic import BaseModel, Field

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from ..assets import AssetsInfo
from ..core.retriver import DocsRetriever, DEVICE
from ..core.llm_core import run_llm_loop, LLMExecutionError, SystemError
from .tools import (
    write_notes, discard_slot, get_more_raw_content,
    set_init_content, leave_message,
    set_vectorstore, get_global_state, reset_global_state
)
from .prompt import RESEARCH_PROMPT

logger = logging.getLogger("TestGen.researcher")

class LLMOutput(BaseModel):
    """LLM输出格式"""
    status: str = Field(description="状态: completed 或 failed")
    message: str = Field(default="", description="状态消息或错误信息")


class Researcher:
    def __init__(self, pdf_path: str, chunk_size: int = 2000):
        """
        初始化Researcher
        
        Args:
            pdf_path: PDF文件路径
            chunk_size: 每次读取的字符数
        """
        self.pdf_path = pdf_path
        self.chunk_size = chunk_size
        self.vectorstore = None
        self.retriever = None
        
    def _load_pdf_content(self) -> str:
        """加载PDF文件内容"""
        logger.info(f"Loading PDF: {self.pdf_path}")
        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()
        
        # 合并所有页面的内容
        full_text = "\n\n".join([doc.page_content for doc in documents])
        logger.info(f"Loaded PDF, total characters: {len(full_text)}")
        return full_text
    
    def _initialize_vectorstore(self, force_rebuild: bool = False):
        """初始化向量数据库
        
        重要说明：
        - 这里只初始化向量数据库，不进行任何分块操作
        - 所有文档块都由LLM通过write_notes工具进行语义分块后直接添加
        - write_notes使用add_documents方法，该方法不会重新分块，直接将Document原样存储
        - DocsRetriever的chunk_size和chunk_overlap参数在这里不会被使用
        """
        logger.info(f"Initializing vectorstore at {AssetsInfo.pdfs_vector_path}")
        
        # 只使用DocsRetriever来获取embeddings和保存/加载功能
        # chunk_size和chunk_overlap参数在这里不会被使用（仅用于兼容DocsRetriever接口）
        self.retriever = DocsRetriever(
            docs_path=AssetsInfo.pdfs_path,
            vector_path=AssetsInfo.pdfs_vector_path,
            chunk_size=500,  # 不会被使用，LLM已完成分块
            chunk_overlap=100  # 不会被使用，LLM已完成分块
        )
        
        if not force_rebuild and os.path.exists(AssetsInfo.pdfs_vector_path):
            if self.retriever.load_vectorstore():
                logger.info("Loaded existing vectorstore")
                self.vectorstore = self.retriever.vectorstore
                set_vectorstore(self.vectorstore)
                return
        
        # 创建新的向量数据库（使用占位符文档）
        logger.info("Creating new vectorstore")
        from langchain_community.vectorstores import FAISS
        from langchain_core.documents import Document
        # 创建一个占位符文档以初始化向量数据库
        placeholder_doc = Document(page_content="placeholder", metadata={})
        self.vectorstore = FAISS.from_documents(
            documents=[placeholder_doc],
            embedding=self.retriever.embeddings
        )
        # 删除占位符文档 - 获取docstore_id并删除
        if hasattr(self.vectorstore, 'index_to_docstore_id') and self.vectorstore.index_to_docstore_id:
            # index_to_docstore_id 是一个字典，key是索引，value是docstore_id
            if len(self.vectorstore.index_to_docstore_id) > 0:
                # 获取第一个docstore_id
                first_docstore_id = list(self.vectorstore.index_to_docstore_id.values())[0]
                self.vectorstore.delete([first_docstore_id])
        self.retriever.vectorstore = self.vectorstore
        set_vectorstore(self.vectorstore)
    
    async def _process_chunk(self, content: str, book_name: str, leave_msg: str = "") -> dict:
        """处理一个内容块"""
        reset_global_state()
        state = get_global_state()
        state["current_content"] = content
        state["leave_message"] = leave_msg
        
        tool_list = [
            write_notes,
            discard_slot,
            get_more_raw_content,
            set_init_content,
            leave_message
        ]
        
        # 不预先截断content，让LLM根据语义边界自行处理
        # LLM会通过write_notes工具的参数限制（2000字符）来控制内容长度
        format_args = {
            "content": content,  # 传递完整内容，让LLM按语义边界处理
            "leave_message": f"\n备注: {leave_msg}" if leave_msg else ""
        }
        
        result = await run_llm_loop(
            prompt_template=RESEARCH_PROMPT,
            output_pydantic=LLMOutput,
            format_args=format_args,
            tool_list=tool_list
        )
        
        return result
    
    async def process_pdf(self, force_rebuild: bool = False):
        """处理PDF文件"""
        # 初始化向量数据库
        self._initialize_vectorstore(force_rebuild=force_rebuild)
        
        # 加载PDF内容
        full_content = self._load_pdf_content()
        
        # 按chunk_size分块处理
        position = 0
        book_name = os.path.basename(self.pdf_path).replace('.pdf', '')
        leave_message = ""
        
        while position < len(full_content):
            # 检查是否有设置下一轮初始内容
            state = get_global_state()
            used_next_init = False
            if state.get('next_init_content'):
                # 如果有设置初始内容，使用它作为当前块
                chunk = state['next_init_content']
                state['next_init_content'] = ""
                used_next_init = True
                logger.info(f"Using next_init_content as chunk, length: {len(chunk)}")
            else:
                # 正常读取下一个chunk
                chunk = full_content[position:position + self.chunk_size]
            
            logger.info(f"Processing chunk at position {position}/{len(full_content)}, chunk length: {len(chunk)}")
            
            try:
                result = await self._process_chunk(chunk, book_name, leave_message)
                
                # LLM返回failed状态，这是LLM执行错误，继续处理下一段
                if result.get('status') == 'failed':
                    logger.warning(f"LLM返回failed状态: {result.get('message', '')}")
                    logger.info("清空状态，继续处理下一段内容")
                    # 清空状态
                    state = get_global_state()
                    state['next_init_content'] = ""
                    state['leave_message'] = ""
                    leave_message = ""
                    # 移动到下一段
                    if not used_next_init:
                        position += self.chunk_size
                    continue
                
                # 更新leave_message
                state = get_global_state()
                if state.get('leave_message'):
                    leave_message = state['leave_message']
                
            except LLMExecutionError as e:
                # LLM执行错误（JSON解析失败、工具调用失败等），继续处理下一段
                logger.warning(f"LLM执行错误（可恢复）: {e}")
                logger.info("清空状态，继续处理下一段内容")
                # 清空状态
                state = get_global_state()
                state['next_init_content'] = ""
                state['leave_message'] = ""
                leave_message = ""
                # 移动到下一段
                if not used_next_init:
                    position += self.chunk_size
                continue
                
            except SystemError as e:
                # 系统错误（API调用失败等），停止整个任务
                logger.error(f"系统错误（不可恢复）: {e}")
                raise  # 重新抛出，让上层处理
            
            except Exception as e:
                # 其他未知错误，根据错误类型判断
                error_str = str(e).lower()
                # 判断是否是系统级错误
                if any(keyword in error_str for keyword in ['api', 'network', 'connection', 'timeout', 'authentication', 'file', 'permission']):
                    logger.error(f"系统错误（不可恢复）: {e}")
                    raise SystemError(f"系统错误: {e}") from e
                else:
                    # 其他错误视为LLM执行错误
                    logger.warning(f"未知错误，视为LLM执行错误（可恢复）: {e}")
                    logger.info("清空状态，继续处理下一段内容")
                    state = get_global_state()
                    state['next_init_content'] = ""
                    state['leave_message'] = ""
                    leave_message = ""
                    if not used_next_init:
                        position += self.chunk_size
                    continue
            
            # 如果使用了next_init_content，不移动position；否则移动到下一个位置
            if not used_next_init:
                position += self.chunk_size
            
            # 检查是否还有更多内容
            if position >= len(full_content):
                break
        
        # 保存向量数据库
        self.retriever.save_vectorstore()
        logger.info("Processing completed and vectorstore saved")


def main():
    """测试函数"""
    pdf_path = r"D:\workspace\repo\doc\pdfs\Hypothesis.pdf"
    researcher = Researcher(pdf_path, chunk_size=2000)
    asyncio.run(researcher.process_pdf(force_rebuild=False))


if __name__ == "__main__":
    main()
