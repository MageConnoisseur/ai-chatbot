import os
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(".")  # index everything in your repo

SKIP_FOLDERS = [
    "conversation_save_files",
    "chat_logs",
    "logs",
    "venv",
    ".git",
    "__pycache__",
    "embeddings"
]

INDEX_PATH = "knowledge_base/embeddings/index.json"

#clarifying which extensions are allowed
ALLOWED_EXTENSIONS = {
    ".py", ".txt", ".md", ".json", ".yaml", ".yml",
    ".js", ".ts", ".html", ".css", ".c", ".cpp", ".java"
}

#=============================================================
#Embed text helper function called for each chunk in chunks
#=============================================================
def embed_text(text):
    """Send text to Ollama and return an embedding vector."""
    result = subprocess.run(
        ["ollama", "run", "embeddinggemma:300m"],
        input=text.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    try:
        data = json.loads(result.stdout.decode())
        return data  # embeddinggemma returns a raw list
    except Exception as e:
        print("Embedding parse error:", e)
        return None

#=============================================================
#Auto chunker with chunk size
#=============================================================
def chunk_text(text, max_chars=800, chunk_overlap = 200):
    """Simple fixed-size chunking with overlap to include context"""
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + max_chars])
        start += max_chars - chunk_overlap
    return chunks

#=============================================================
#Main indexer function
#=============================================================
def index_files():
    all_chunks = []

    print("Walking project folders...\n")

    for root, dirs, files in os.walk(PROJECT_ROOT):

        # skip unwanted folders
        if any(skip in root for skip in SKIP_FOLDERS):
            continue

        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue  # skip binary, images, etc.

            filepath = Path(root) / filename
            print(f"Indexing: {filepath}")

            try:
                text = filepath.read_text(errors="ignore")
            except:
                print(f"Could not read file: {filepath}")
                continue

            chunks = chunk_text(text)

            for i, chunk in enumerate(chunks):
                embed = embed_text(chunk)
                if embed:
                    all_chunks.append({
                        "id": f"{filepath}:{i}",
                        "source": filename,
                        "text": chunk,
                        "embedding": embed
                    })

    # save output
    os.makedirs("knowledge_base/embeddings", exist_ok=True)
    with open(INDEX_PATH, "w") as f:
        json.dump(all_chunks, f, indent=2)

    print("\nIndexing complete!")
    print(f"Total chunks: {len(all_chunks)}")

if __name__ == "__main__":
    index_files()
