"""
提取向量数据库中的所有章节名称并保存到文件

功能：
- 从向量数据库中提取所有唯一的章节名称
- 将章节名称保存到 chapters.txt 文件中
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.retriver import DocsRetriever
from src.assets import AssetsInfo


def extract_chapter_names():
    """提取所有章节名称并保存到文件"""
    print("正在加载向量数据库...")
    
    # 创建Retriever实例
    retriever = DocsRetriever(
        docs_path=AssetsInfo.pdfs_path,
        vector_path=AssetsInfo.pdfs_vector_path,
        chunk_size=500,
        chunk_overlap=100
    )
    
    # 加载向量数据库
    if not retriever.load_vectorstore():
        print("错误: 无法加载向量数据库")
        return
    
    vectorstore = retriever.vectorstore
    
    # 获取所有文档
    total_docs = len(vectorstore.index_to_docstore_id)
    if total_docs == 0:
        print("向量数据库为空")
        return
    
    print(f"找到 {total_docs} 个文档，正在提取章节名称...")
    
    # 收集所有唯一的章节名称
    chapter_names = set()
    
    for doc_id in vectorstore.index_to_docstore_id.values():
        doc = vectorstore.docstore.search(doc_id)
        chapter_name = doc.metadata.get('chapter_name', 'Unknown')
        if chapter_name and chapter_name != 'Unknown':
            chapter_names.add(chapter_name)
    
    # 按字母顺序排序
    sorted_chapters = sorted(chapter_names)
    
    # 输出到文件
    output_file = Path(__file__).parent / "chapters.txt"
    print(f"正在写入文件: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chapter_name in sorted_chapters:
            f.write(f"{chapter_name}\n")
    
    print(f"完成！共提取 {len(sorted_chapters)} 个唯一的章节名称")
    print(f"文件已保存到: {output_file}")


if __name__ == "__main__":
    extract_chapter_names()

