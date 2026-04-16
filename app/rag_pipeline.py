import requests
import os
from app.retriever import search
from app.prompts import RAG_PROMPT

from app.security.iam_analyzer import analyze_iam_policy
from app.security.log_analyzer import analyze_log
from app.security.misconfig_detector import detect_misconfig


def detect_input_type(query):
    """
    Detect what user provided
    """

    if "{" in query and "Action" in query:
        return "iam"

    if "User:" in query and "Action:" in query:
        return "log"

    return "general"


def build_context(docs):
    context = ""
    for doc in docs:
        context += f"\nSource: {doc['source']}\n{doc['content']}\n"
    return context


def query_rag(query):
    """
    Enhanced RAG with security intelligence
    """

    input_type = detect_input_type(query)

    # 🔐 IAM Analysis
    if input_type == "iam":
        analysis = analyze_iam_policy(query)
        return {
            "answer": f"IAM Policy Analysis:\n{analysis}",
            "sources": ["Generated Analysis"]
        }

    # 📊 Log Analysis
    if input_type == "log":
        analysis = analyze_log(query)
        return {
            "answer": f"Log Analysis:\n{analysis}",
            "sources": ["Generated Analysis"]
        }

    # 📚 Normal RAG
    docs = search(query)
    context = build_context(docs)

    prompt = RAG_PROMPT.format(
        context=context,
        question=query
    )

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()

    return {
        "answer": result["response"],
        "sources": [doc["source"] for doc in docs]
    }
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
