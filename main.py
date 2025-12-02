import os
import logging
from rich.logging import RichHandler

from src.core.retriver import DocsRetriever
from src.assets import AssetsInfo

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(message)s",
    datefmt="[%H:%M:%S]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,   # 异常时用 rich 的彩色 traceback
            markup=True,            # 支持 rich 的 markup 语法
            show_time=False,        # 这里时间交给 format 的 %(asctime)s 管
            show_path=True,        # 如果想在左侧显示路径，可以改 True
        )
    ],
)
logger = logging.getLogger("TestGen")
logger.setLevel(logging.DEBUG)


def main():
    logger.info("Creating retriever instance...")
    retriever = DocsRetriever(
        docs_path=AssetsInfo.doc_path,
        vector_path=AssetsInfo.vector_path,
        chunk_size=2000,
        chunk_overlap=300,
    )
    
    # 初始化向量数据库
    print("\n初始化向量数据库...")
    retriever.initialize(force_rebuild=False)
    
    # 测试查询
    test_queries = [
        "为我提供一个简单的使用Hypothesis的示例",
        "Type hints for composite这一节有哪些内容",
    ]
    
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\nquery {i}/{len(test_queries)}: {query}\n")
        logger.info("-" * 80)        
        # 执行搜索
        results = retriever.search(query, k=2)
        for i, doc in enumerate(results, 1):
            content = doc.page_content.strip()
            logger.info(f"{content}\n")
            logger.info("-" * 80)  


if __name__ == "__main__":
    main()
