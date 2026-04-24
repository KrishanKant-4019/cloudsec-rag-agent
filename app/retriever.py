import os
import pickle
import re
from collections import Counter
from functools import lru_cache

import numpy as np

from app.config import get_settings
from app.embeddings import get_embeddings
from app.utils import load_documents


settings = get_settings()
VECTORSTORE_DIR = str(settings["vectorstore_dir"])
LEGACY_VECTOR_PATH = os.path.join(VECTORSTORE_DIR, "faiss_index.pkl")
INDEX_PATH = os.path.join(VECTORSTORE_DIR, "faiss.index")
DOCS_PATH = os.path.join(VECTORSTORE_DIR, "documents.pkl")


def _tokenize(text):
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def _keyword_search(query, top_k=3):
    documents = load_documents()
    query_tokens = Counter(_tokenize(query))

    scored = []
    for doc in documents:
        doc_tokens = Counter(_tokenize(doc["content"]))
        score = sum(query_tokens[token] * doc_tokens.get(token, 0) for token in query_tokens)
        scored.append((score, doc))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for score, doc in scored if score > 0][:top_k]


def _persist_documents(documents):
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    with open(DOCS_PATH, "wb") as file_obj:
        pickle.dump(documents, file_obj)


def _load_persisted_documents():
    if not os.path.exists(DOCS_PATH):
        return None
    with open(DOCS_PATH, "rb") as file_obj:
        return pickle.load(file_obj)


def create_vectorstore():
    documents = load_documents()
    if not documents:
        return None, []

    texts = [doc["content"] for doc in documents]
    embeddings = np.array(get_embeddings(texts), dtype="float32")
    _persist_documents(documents)

    try:
        import faiss

        index = faiss.IndexFlatL2(int(embeddings.shape[1]))
        index.add(embeddings)
        faiss.write_index(index, INDEX_PATH)
        _load_vectorstore.cache_clear()
        return index, documents
    except Exception:
        np.save(os.path.join(VECTORSTORE_DIR, "embeddings.npy"), embeddings)
        _load_vectorstore.cache_clear()
        return embeddings, documents


@lru_cache(maxsize=1)
def _load_vectorstore():
    if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH):
        try:
            import faiss

            return faiss.read_index(INDEX_PATH), _load_persisted_documents()
        except Exception:
            pass

    embeddings_path = os.path.join(VECTORSTORE_DIR, "embeddings.npy")
    if os.path.exists(embeddings_path) and os.path.exists(DOCS_PATH):
        return np.load(embeddings_path), _load_persisted_documents()

    if os.path.exists(LEGACY_VECTOR_PATH):
        try:
            with open(LEGACY_VECTOR_PATH, "rb") as file_obj:
                return pickle.load(file_obj)
        except Exception:
            pass

    return create_vectorstore()


def search(query, top_k=3):
    if not query.strip():
        return []

    try:
        index, documents = _load_vectorstore()
        if not documents:
            return []

        query_embedding = np.array(get_embeddings([query]), dtype="float32")
        if isinstance(index, np.ndarray):
            scores = np.dot(index, query_embedding[0])
            ranked = np.argsort(scores)[::-1][:top_k]
            return [documents[i] for i in ranked if 0 <= i < len(documents)]

        _, indices = index.search(query_embedding, top_k)
        return [documents[i] for i in indices[0] if 0 <= i < len(documents)]
    except Exception:
        return _keyword_search(query, top_k=top_k)
