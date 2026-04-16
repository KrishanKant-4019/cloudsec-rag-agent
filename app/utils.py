import os

def load_documents(data_path="data"):
    documents = []

    for root, _, files in os.walk(data_path):
        for file in files:
            file_path = os.path.join(root, file)

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