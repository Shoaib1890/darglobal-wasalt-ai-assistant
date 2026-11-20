import logging
import re
import hashlib
from typing import List, Union
import numpy as np

logger = logging.getLogger(__name__)

DIM = 384

def _hash_token(token: str, seed: int) -> int:
    h = hashlib.md5(f"{seed}:{token}".encode("utf-8")).digest()
    return int.from_bytes(h[:4], "little", signed=True)

class MultilingualEmbedder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MultilingualEmbedder, cls).__new__(cls)
            logger.info("Initializing ultra-lightweight multilingual embedder (zero-PyTorch, <35MB RAM).")
        return cls._instance

    def _embed_single(self, text: str) -> np.ndarray:
        text_clean = text.lower()
        words = re.findall(r'[\w\u0600-\u06FF]+', text_clean)
        tokens = list(words)
        
        # Sub-word character n-grams (3-4 chars) for Arabic, Russian, and English stems
        for w in words:
            if len(w) >= 3:
                for n in (3, 4):
                    for i in range(len(w) - n + 1):
                        tokens.append(f"__{w[i:i+n]}__")

        vec = np.zeros(DIM, dtype=np.float32)
        for t in tokens:
            idx = abs(_hash_token(t, 42)) % DIM
            sign = 1.0 if _hash_token(t, 84) > 0 else -1.0
            vec[idx] += sign

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generates normalized 384-dimensional dense vector embeddings for text."""
        if isinstance(texts, str):
            texts = [texts]
        vecs = [self._embed_single(t) for t in texts]
        return np.array(vecs, dtype=np.float32)

embedder = MultilingualEmbedder()
