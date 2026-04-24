import os
from functools import lru_cache

from app.config import get_settings


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

                    documents.append({
                        "content": content,
                        "source": file_path
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return documents
