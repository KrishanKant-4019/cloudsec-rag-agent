import os
import pickle
import re
from collections import Counter

import numpy as np

from app.embeddings import get_embeddings
from app.utils import load_documents

VECTORSTORE_DIR = "vectorstore"
LEGACY_VECTOR_PATH = os.path.join(VECTORSTORE_DIR, "faiss_index.pkl")
INDEX_PATH = os.path.join(VECTORSTORE_DIR, "faiss.index")
DOCS_PATH = os.path.join(VECTORSTORE_DIR, "documents.pkl")


def _ensure_vectorstore_dir():
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)


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
    results = [doc for score, doc in scored if score > 0]

    return results[:top_k]


def create_vectorstore():
    """
    Create and persist a FAISS index from local documents.
    """
    import faiss

    documents = load_documents()
    texts = [doc["content"] for doc in documents]

    embeddings = np.array(get_embeddings(texts), dtype="float32")
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    _ensure_vectorstore_dir()
    faiss.write_index(index, INDEX_PATH)

    with open(DOCS_PATH, "wb") as file_obj:
        pickle.dump(documents, file_obj)


def load_vectorstore():
    """
    Load the FAISS index and documents from disk.
    """
    import faiss

    if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(DOCS_PATH, "rb") as file_obj:
            documents = pickle.load(file_obj)
        return index, documents

    if os.path.exists(LEGACY_VECTOR_PATH):
        try:
            with open(LEGACY_VECTOR_PATH, "rb") as file_obj:
                index, documents = pickle.load(file_obj)
            return index, documents
        except ModuleNotFoundError:
            create_vectorstore()
            return load_vectorstore()

    create_vectorstore()
    return load_vectorstore()


def search(query, top_k=3):
    """
    Search similar documents, falling back to keyword search if semantic
    retrieval is unavailable in the current environment.
    """
    try:
        index, documents = load_vectorstore()
        query_embedding = np.array(get_embeddings([query]), dtype="float32")
        _, indices = index.search(query_embedding, top_k)

        results = []
        for doc_index in indices[0]:
            if 0 <= doc_index < len(documents):
                results.append(documents[doc_index])

        if results:
            return results
    except Exception:
        pass

    return _keyword_search(query, top_k=top_k)
