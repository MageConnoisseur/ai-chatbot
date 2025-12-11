# retriever.py
import json
import subprocess
from pathlib import Path
from math import sqrt
from typing import List, Dict, Any, Tuple, Optional

#Default index path 
INDEX_PATH = Path("knowledge_base/embeddings/index.json")

#Ollama embedding model to call for queries
EMBEDDING_MODEL = "embeddinggemma:300m"

#Small epsilon to avoid division by zero
_EPS = 1e-15

#============================================================
#Load / validate index
#============================================================
def load_index(path: Path = INDEX_PATH) -> List[Dict[str, Any]]:
    """
    Load the index JSON file and validate basic structure.

    Returns unchanged list of chunks(except for normalized)
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Index file not found: {path}")
    
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError ("Index file must contain a JSON list of chunks")
    
    #Basic validation / normalization
    cleaned = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            continue
        emb = entry.get("embedding")
        if emb is None: #skip entries without embeddings
            continue

        #if embedding is nested dict or wrapped, try to normalise here
        if isinstance(emb, dict) and "embedding" in emb:
            emb = emb["embedding"]
        if not isinstance(emb, list):#skip invalid embeddings
            continue

        cleaned.append({
            "id": entry.get("id", f"{entry.get('file', 'unknown')}:{i}"),
            "file": entry.get("file") or entry.get("source"),
            "text": entry.get("text", ""),
            "embedding": [float(x) for x in emb]
        })

    return cleaned

#=========================================================================
# Embed the query text
#=========================================================================

def embed_query(text: str, model: str = EMBEDDING_MODEL) -> Optional[List[float]]:
    """Call ollama to produce an embedding for 'text' 
    
    
    returns a list of floats or None on parse error.
    """

    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input = text.encode("utf-8"),
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            check = False  #already handling non 0 error
            )

    except FileNotFoundError:
        raise RuntimeError("Could not run \'ollama\' -- is it installed and on PATH?")
    
    out = result.stdout.decode("utf-8").strip()
    if not out:
        #sometimes stderr contains info
        #return None so caller can handle
        return None
    
    try:
        data = json.loads(out)
    except Exception as e:
        #unexpected format
        return None
    
    # handle dict with "embedding"
    if isinstance(data, dict) and "embedding" in data:
        emb = data["embedding"]
    #handle if model returns an top level list only
    elif isinstance(data,list):
        emb = data
    else:
        #unknown format
        return None
    
    try:
        return [float(x) for x in emb]
    except Exception:
        return None
    
    #==================================================================
    # Vector Helpers
    #===================================================================
def dot(a: List[float], b: List[float]) -> float:
    """returns a product of two equal length vectors."""
    return sum(x*y for x, y in zip(a,b))
    
def norm(a: List[float]) -> float:
    """Euclidean norm."""
    return sqrt(sum(x * x for x in a))

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Compute cosine similarity in a safe way.
    Returns value in [-1, 1].
    """
    da = dot(a, b)
    na = norm(a)
    nb = norm(b)
    denom = (na * nb) if (na > _EPS and nb > _EPS) else _EPS
    return da / denom


def score_chunks(query_emb: List[float],
                 chunks: List[Dict[str, Any]],
                 top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
    """
    Score all chunks by cosine similarity to query_emb
    
    returns the top_k matches as list of (score, chunk) sorted desc order.
    """
    scored = []
    for chunk in chunks:
        emb = chunk.get("embedding")
        if not emb:
            continue
        #If embedding lengths mismatch, skip to avoid error
        if len(emb) != len(query_emb):
            #maybe resize here, skip for now
            continue
        score = cosine_similarity(query_emb, emb)
        scored.append((score,chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]

#==============================================================================
#Convenience top level retrieve function
#==============================================================================

def retrieve(query: str,
             index_path: Path = INDEX_PATH,
             ret_model: str = EMBEDDING_MODEL,
             top_k_ret: int = 5) -> List[Dict[str, Any]]:
    chunks = load_index(index_path)
    q_emb = embed_query(query, model=ret_model)
    if q_emb is None:
        raise RuntimeError("Failed to produce query embedding")

    top = score_chunks(q_emb, chunks, top_k=top_k_ret)
    # attach score to each returned chunk for convienience
    results = []
    for score, chunk in top:
        r = dict(chunk) #shallow copy
        r["score"] = float(score)
        results.append(r)
    return results

#==============================================================
#format rsults for prompt
#==============================================================

def format_for_prompt(results: List[Dict[str, Any]], char_length: int = 1000) -> str:
    """
    Turn a list of retrived chunk dicts into a single context string
    Truncates each chunk to 'chars'
    
    """
    parts = []
    for r in results:
        header = f"--- {Path(r.get('file', 'unknown')).name} (score ={r.get('score', 0):.4f})"
        snippet = (r.get("text","")[:char_length]).strip()
        parts.append(header)
        parts.append(snippet)
    return "\n\n".join(parts)
    

#======================================================================
#Local tester
#======================================================================
def _test_local():
    print("Loading index:", INDEX_PATH)
    chunks = load_index()
    print("Chunks loaded:", len(chunks))
    query = "How do I create a Font in tkinter?"
    results = retrieve(query, top_k_ret=5)
    print("Top results:")
    for r in results:
        print(r["file"], r["score"], r["text"][:120].replace("\n"," "))

if __name__ == "__main__":
    _test_local()
