import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.guider.read_all_guidelines import read_guidelines
from src.assets import AssetsInfo
from src.core import LocalEmbeddings, DEVICE
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from rich.logging import RichHandler
import logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(message)s",
    datefmt="[%H:%M:%S]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=False,
            show_path=True,
        )
    ],
)
logger = logging.getLogger("TestGen")
logger.setLevel(logging.DEBUG)


def build_notes_vectorstore():
    notes_path = Path(AssetsInfo.guidelines_json_path)
    data = json.loads(notes_path.read_text(encoding="utf-8"))
    documents = [
        Document(
            page_content=item.get("content", ""),
            metadata={
                "book_name": item.get("book_name", ""),
                "abstract": item.get("abstract", ""),
            },
        )
        for item in data
    ]
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    embeddings = LocalEmbeddings(
        model_path=AssetsInfo.local_embeddings_path,
        model_repo=AssetsInfo.local_embeddings_repo,
        device=DEVICE,
        hf_mirror=AssetsInfo.local_embeddings_auto_download,
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vector_dir = Path(AssetsInfo.vector_path)
    vector_dir.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(vector_dir))
    logger.info("Guideline vectorstore saved to %s", vector_dir)


def main():
    """Run the end-to-end guideline build without extra parameters."""
    read_guidelines("")
    build_notes_vectorstore()


if __name__ == "__main__":
    main()
