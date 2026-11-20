import logging
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)

class MultilingualEmbedder:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MultilingualEmbedder, cls).__new__(cls)
            logger.info(f"Loading multilingual embedding model: {EMBEDDING_MODEL_NAME}")
            cls._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info("Multilingual embedding model loaded successfully.")
        return cls._instance

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generates normalized vector embeddings for a string or list of strings."""
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings

embedder = MultilingualEmbedder()
