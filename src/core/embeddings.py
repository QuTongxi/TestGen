import logging
import os
from typing import List

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download

logger = logging.getLogger("TestGen.embeddings")

class LocalEmbeddings(Embeddings):
    def __init__(self,
        model_path: str,
        model_repo: str,
        device: str,
        batch_size: int = 32,
        hf_mirror: bool = True,
    ):
        self.model_path = model_path
        self.device = device
        self.batch_size = batch_size
        self.model_repo = model_repo
        self.model = None
        self.hf_mirror = hf_mirror
        self._download_model()
        self._load_model()

    def _download_model(self):
        logger.info(f"Downloading model {self.model_repo} to {self.model_path}")
        os.makedirs(self.model_path, exist_ok=True)
        snapshot_download(
            repo_id=self.model_repo,
            local_dir=self.model_path,
            force_download=False,
            endpoint="https://hf-mirror.com" if self.hf_mirror else "https://huggingface.co",
        )
        logger.info(f"Model downloaded successfully.")
        
    def _load_model(self):
        logger.debug(f"Loading model ...")
        if self.model is None:
            self.model = SentenceTransformer(
                self.model_path,
                device=self.device,
                tokenizer_kwargs={"padding_side": "left"},
            )
            logger.debug("Model loaded successfully.")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        try:
            embedding = self.model.encode(
                text,
                prompt_name="query",
                convert_to_numpy=True,
            )
        except Exception:
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
            )
        return embedding.tolist()
        

