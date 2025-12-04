import os

class Assets:
    local_embeddings_path: str = r"D:\workspace\TestGen\embeddings\Qwen3-Embedding-0.6B"
    local_embeddings_repo: str = r"Qwen/Qwen3-Embedding-0.6B"
    # local_embeddings_repo: str = r"BAAI/bge-m3"
    local_embeddings_auto_download: bool = False

    # 指南文档与向量库
    doc_path: str = r"D:\workspace\TestGen\doc\guide\markdowns"
    vector_path: str = r"D:\workspace\TestGen\doc\guide\vectorstore"
    guidelines_json_path: str = r"D:\workspace\TestGen\doc\guide\guidelines_notes.json"
    good_guide_path: str = r"D:\workspace\TestGen\doc\guide\good_guide"

    # OpenAI配置
    openai_model: str = 'qwen3-max'
    openai_api_url: str = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    openai_api_key: str = "sk-c0d3d24b6eab4b9fbbf654c2a8817980"

    # PDF相关路径
    pdfs_path: str = r"D:\workspace\TestGen\doc\pdfs"
    pdfs_vector_path: str = r"D:\workspace\TestGen\doc\pdfs\vectorstore"

AssetsInfo = Assets()