import os
from functools import lru_cache

from app.config import get_settings


CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


def _chunk_text(content):
    if len(content) <= CHUNK_SIZE:
        return [content]

    chunks = []
    start = 0
    while start < len(content):
        end = start + CHUNK_SIZE
        chunk = content[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(content):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks


@lru_cache(maxsize=1)
def load_documents(data_path=None):
    settings = get_settings()
    base_path = data_path or str(settings["data_dir"])
    documents = []
    allowed_extensions = {
        ".txt", ".md", ".json", ".yaml", ".yml", ".log", ".cfg", ".conf",
        ".ini", ".tf", ".hcl", ".py", ".js", ".ts", ".sql", ".xml", ".csv",
    }

    for root, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            extension = os.path.splitext(file)[1].lower()
            if extension and extension not in allowed_extensions:
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                    for index, chunk in enumerate(_chunk_text(content), start=1):
                        documents.append({
                            "content": chunk,
                            "source": f"{file_path}#chunk-{index}"
                        })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return documents
