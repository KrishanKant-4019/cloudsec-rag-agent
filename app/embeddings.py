import hashlib
from functools import lru_cache

import numpy as np


EMBED_DIMENSION = 384


@lru_cache(maxsize=1)
def _load_sentence_transformer():
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    except Exception:
        return None


def _hash_embedding(text: str) -> np.ndarray:
    vector = np.zeros(EMBED_DIMENSION, dtype="float32")
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], byteorder="big") % EMBED_DIMENSION
        weight = (digest[4] / 255.0) + 0.5
        vector[index] += weight

    norm = np.linalg.norm(vector)
    if norm > 0:
        vector /= norm
    return vector


def get_embeddings(texts):
    model = _load_sentence_transformer()
    if model is not None:
        return model.encode(texts, normalize_embeddings=True)
    return np.vstack([_hash_embedding(text) for text in texts])
