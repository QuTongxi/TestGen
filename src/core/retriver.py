import os
import logging
from typing import List, Optional

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..assets import AssetsInfo
from .embeddings import LocalEmbeddings

logger = logging.getLogger("TestGen.retriver")

DEVICE = "cpu"


class DocsRetriever:
    def __init__(self, docs_path, vector_path, chunk_size: int = 500, chunk_overlap: int = 100):
        self.docs_path = docs_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_store_path = vector_path
        
        logger.info(f"using {DEVICE} for embeddings...")
        self.embeddings = LocalEmbeddings(
            model_path=AssetsInfo.local_embeddings_path,
            model_repo = AssetsInfo.local_embeddings_repo,
            device= DEVICE
        )
        self.vectorstore = None

    def load_documents(self) -> List[Document]:
        logger.info(f"Loading Markdown documents from {self.docs_path} ...")
        
        # 使用 DirectoryLoader 递归加载所有 .md 文件
        # 使用 TextLoader 替代 UnstructuredMarkdownLoader（更轻量，无需额外依赖）
        loader = DirectoryLoader(
            self.docs_path,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=True,
            use_multithreading=True,
            silent_errors=True  # 忽略无法读取的文件
        )
        
        documents = loader.load()
        logger.debug(f"Successfully loaded {len(documents)} documents.")
        
        # 为每个文档添加额外的元数据
        for doc in documents:
            # 提取相对路径作为文档标识
            if 'source' in doc.metadata:
                rel_path = os.path.relpath(doc.metadata['source'], self.docs_path)
                doc.metadata['relative_path'] = rel_path
                doc.metadata['file_name'] = os.path.basename(rel_path)
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        logger.info(f"Splitting documents into chunks, chunk_size={self.chunk_size}, chunk_overlap={self.chunk_overlap} ...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["###", "####", "#####", "######", ""]
        )
        
        splits = text_splitter.split_documents(documents)
        logger.info(f"Successfully split {len(splits)} documents into chunks.")
        
        return splits
    
    def build_vectorstore(self, documents: List[Document], batch_size: int = 100) -> FAISS:
        logger.info(f"Building vectorstore with {len(documents)} documents, batch_size={batch_size} ...")
        
        # 分批处理以显示进度
        if len(documents) > batch_size:
            # 第一批创建vectorstore
            logger.info(f"Processing batch 1/{len(documents)//batch_size + 1} ...")
            vectorstore = FAISS.from_documents(
                documents=documents[:batch_size],
                embedding=self.embeddings
            )
            
            # 后续批次添加到vectorstore
            for i in range(batch_size, len(documents), batch_size):
                batch_num = i // batch_size + 1
                total_batches = len(documents) // batch_size + 1
                logger.info(f"Processing batch {batch_num}/{total_batches} ...")
                
                batch_docs = documents[i:i+batch_size]
                batch_vectorstore = FAISS.from_documents(
                    documents=batch_docs,
                    embedding=self.embeddings
                )
                vectorstore.merge_from(batch_vectorstore)
        else:
            vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
        
        logger.info(f"Successfully built vectorstore with {len(documents)} documents.")
        
        return vectorstore
    
    def save_vectorstore(self, path: Optional[str] = None):
        logger.info(f"Saving vectorstore to {path} ...")
        if self.vectorstore is None:
            logger.error("Vectorstore is not initialized, cannot save.")
            return
        
        save_path = path or self.vector_store_path
        if save_path is None:
            logger.error("No save path specified, skipping save.")
            return
        
        self.vectorstore.save_local(save_path)
        logger.info(f"Successfully saved vectorstore to {save_path}.")
    
    def load_vectorstore(self, path: Optional[str] = None):
        logger.info(f"Loading vectorstore from {path} ...")
        load_path = path or self.vector_store_path
        if load_path is None or not os.path.exists(load_path):
            logger.error(f"Vectorstore path does not exist: {load_path}")
            return False
        
        self.vectorstore = FAISS.load_local(
            load_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info(f"Successfully loaded vectorstore from {load_path}.")
        return True
    
    def initialize(self, force_rebuild: bool = False):
        logger.info(f"Initializing vectorstore, force_rebuild={force_rebuild} ...")
        if not force_rebuild and self.load_vectorstore():
            logger.info("Using existing vectorstore.")
            return
        
        # 加载文档
        documents = self.load_documents()
        if not documents:
            logger.error("No documents loaded.")
            return
        
        # 分割文档
        splits = self.split_documents(documents)
        
        # 构建向量数据库
        self.vectorstore = self.build_vectorstore(splits)
        
        # 保存向量数据库
        self.save_vectorstore()
    
    def search(
        self,
        query: str,
        k: int = 5,
        search_type: str = "similarity"
    ) -> List[Document]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            k: 返回的文档数量
            search_type: 检索类型，"similarity" 或 "mmr"
            
        Returns:
            相关文档列表
        """
        if self.vectorstore is None:
            logger.error("Vectorstore is not initialized, please call initialize() first.")
            return []
        
        logger.info(f"Searching for '{query}' returning {k} results ...")
        
        if search_type == "mmr":
            # 使用 MMR (最大边际相关性) 检索
            results = self.vectorstore.max_marginal_relevance_search(query, k=k)
        else:
            # 使用相似度检索
            results = self.vectorstore.similarity_search(query, k=k)
        
        logger.info(f"Search completed, found {len(results)} results.")
        return results
    
    def search_with_score(
        self,
        query: str,
        k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        检索相关文档并返回相似度分数
        
        Args:
            query: 查询文本
            k: 返回的文档数量
            
        Returns:
            (文档, 分数) 元组列表
        """
        if self.vectorstore is None:
            logger.error("Vectorstore is not initialized, please call initialize() first.")
            return []
        
        logger.info(f"Searching with score for '{query}' returning {k} results ...")
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        logger.info(f"Search completed, found {len(results)} results.")
        return results
    
    def get_retriever(self, search_type: str = "similarity", k: int = 5):
        if self.vectorstore is None:
            logger.error("Vectorstore is not initialized, please call initialize() first.")
            return None
        
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k}
        )

