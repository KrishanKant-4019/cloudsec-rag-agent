import hashlib
import logging
import os
from functools import lru_cache
from pathlib import Path

import numpy as np


EMBED_DIMENSION = 384
MODEL_NAME = "all-MiniLM-L6-v2"
logger = logging.getLogger(__name__)


def _local_model_path():
    explicit_path = os.getenv("SENTENCE_TRANSFORMER_MODEL_PATH")
    if explicit_path and Path(explicit_path).exists():
        return explicit_path

    cache_candidates = [
        Path(os.getenv("SENTENCE_TRANSFORMERS_HOME", "")) / MODEL_NAME,
        Path(os.getenv("HF_HOME", "")) / "hub" / "models--sentence-transformers--all-MiniLM-L6-v2",
        Path.home() / ".cache" / "huggingface" / "hub" / "models--sentence-transformers--all-MiniLM-L6-v2",
        Path.home() / ".cache" / "torch" / "sentence_transformers" / "sentence-transformers_all-MiniLM-L6-v2",
    ]
    for path in cache_candidates:
        if str(path) != "." and path.exists():
            return MODEL_NAME
    return None


@lru_cache(maxsize=1)
def _load_sentence_transformer():
    if os.getenv("ENABLE_SENTENCE_TRANSFORMER", "").lower() not in {"1", "true", "yes"}:
        logger.info("SentenceTransformer disabled by default; using hash embeddings.")
        return None

    model_path = _local_model_path()
    if model_path is None:
        logger.info("SentenceTransformer local cache not found; using hash embeddings.")
        return None

    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(model_path, local_files_only=True)
    except Exception:
        logger.warning("SentenceTransformer local load failed; using hash embeddings.", exc_info=True)
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
