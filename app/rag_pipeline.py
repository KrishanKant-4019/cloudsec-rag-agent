from app.agent import run_agent
from app.retriever import search


def query_rag(query: str):
    docs = search(query)
    return {
        "answer": run_agent(query),
        "sources": [doc["source"] for doc in docs],
    }
