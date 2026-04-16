from sentence_transformers import SentenceTransformer

_model = None


def _get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model

def get_embeddings(texts):
    """
    Convert list of texts into embeddings
    """
    return _get_model().encode(texts)
