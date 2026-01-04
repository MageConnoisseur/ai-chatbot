import json
import os
import subprocess
import numpy as np
import time

RAG_REQUIRED_PROMPTS = [
    "Explain the code in this file",
    "Based on the context provided above",
    "Using my Unity C# scripts, how do I implement movement?",
    "Here is an error traceback, help me debug it",
    "Refactor this Python code",
    "What does this function do?",
    "Analyze the following design document",
    "How does my indexer work?",
    "Given the project structure, where should this logic live?",
    "Using the knowledge base, explain this mechanic",
]

def embed_prompt(prompt: str) -> list[float] | None:
    result = subprocess.run(
        ["ollama", "run", "embeddinggemma:300m"],
        input=prompt,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        data = json.loads(result.stdout)
        if isinstance(data, dict) and "embedding" in data:
            return data["embedding"]
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    return None

def normalize(v: list[float]) -> list[float]:
    arr = np.array(v, dtype=np.float32)
    norm = np.linalg.norm(arr)
    return (arr / norm).tolist() if norm != 0 else arr.tolist()

def train_rag_vectors(training_prompts: list[tuple[str, bool]]) -> dict[str, list[list[float]]]:
    rag_vectors = []
    non_rag_vectors = []

    for i, (prompt, requires_rag) in enumerate(training_prompts):
        label = "RAG" if requires_rag else "NO_RAG"
        print(f"[{i+1}/{len(training_prompts)}] Embedding ({label})...")
        emb = embed_prompt(prompt)

        if emb is None:
            print(" ⚠️ Skipped (embedding failed)")
            continue

        emb = normalize (emb)

        if requires_rag:
            rag_vectors.append(emb)
        else:
            non_rag_vectors.append(emb)

    final_dict = {
    "rag": rag_vectors,
    "no_rag": non_rag_vectors
    }

    return final_dict


def save_vectors(vectors: list[list[float]], path: str):
    payload = {
        "model": "embeddinggemma:300m",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "rag_intent_vectors": vectors["rag"],
        "no_rag_intent_vectors": vectors["no_rag"]
    }
    



    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)




if __name__ == "__main__":
    from rag_training_data import TRAINING_PROMPTS
    vectors = train_rag_vectors(TRAINING_PROMPTS)
    save_vectors(vectors, "knowledge_base/embeddings/rag_check_vectors.json")
    print(f"\nTraining complete —"
          f"{len(vectors['rag'])} RAG vectors, "
          f"{len(vectors['no_rag'])} NO_RAG vectors saved"
          )

