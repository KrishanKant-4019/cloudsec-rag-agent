import requests
import os

from app.retriever import search
from app.prompts import RAG_PROMPT

from app.security.iam_analyzer import analyze_iam_policy
from app.security.log_analyzer import analyze_log
from app.security.misconfig_detector import detect_misconfig


# -----------------------------
# ENV CONFIG (MUST BE AT TOP)
# -----------------------------
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


# -----------------------------
# Detect Input Type
# -----------------------------
def detect_input_type(query: str) -> str:
    """
    Detect what type of input user provided
    """

    if "{" in query and "Action" in query:
        return "iam"

    if "User:" in query and "Action:" in query:
        return "log"

    return "general"


# -----------------------------
# Build Context from Docs
# -----------------------------
def build_context(docs):
    context = ""

    for doc in docs:
        context += f"\nSource: {doc['source']}\n"
        context += doc["content"] + "\n"

    return context


# -----------------------------
# LLM CALL WITH FALLBACK
# -----------------------------
def call_llm(prompt: str) -> str:
    """
    Call Ollama LLM with safe fallback (for Render deployment)
    """

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=10  # prevent hanging
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "⚠️ Empty response from LLM")

    except Exception as e:
        # 🚨 IMPORTANT: Render fallback (no Ollama available)
        return (
            "⚠️ LLM is not available in cloud deployment.\n\n"
            "Showing retrieved knowledge only.\n\n"
            f"(Error: {str(e)})"
        )


# -----------------------------
# MAIN RAG PIPELINE
# -----------------------------
def query_rag(query: str):
    """
    Enhanced RAG with:
    - IAM analysis
    - Log analysis
    - Knowledge retrieval
    - LLM fallback
    """

    input_type = detect_input_type(query)

    # 🔐 IAM Analysis
    if input_type == "iam":
        analysis = analyze_iam_policy(query)

        return {
            "answer": f"🔐 IAM Policy Analysis:\n{analysis}",
            "sources": ["Generated Analysis"]
        }

    # 📊 Log Analysis
    if input_type == "log":
        analysis = analyze_log(query)

        return {
            "answer": f"📊 Log Analysis:\n{analysis}",
            "sources": ["Generated Analysis"]
        }

    # ⚙️ Misconfiguration Detection (light heuristic)
    if any(keyword in query.lower() for keyword in ["public", "encryption", "0.0.0.0"]):
        analysis = detect_misconfig(query)

        return {
            "answer": f"⚙️ Misconfiguration Analysis:\n{analysis}",
            "sources": ["Generated Analysis"]
        }

    # 📚 Normal RAG Flow
    docs = search(query)
    context = build_context(docs)

    prompt = RAG_PROMPT.format(
        context=context,
        question=query
    )

    answer = call_llm(prompt)

    return {
        "answer": answer,
        "sources": [doc["source"] for doc in docs]
    }