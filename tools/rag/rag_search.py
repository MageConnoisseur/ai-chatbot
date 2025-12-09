from tools.rag.rag_loader import load_documents

def simple_search(query, limit=3):
    """
    Returns the most relevant documents based on keyword overlap.
    Plan to make this more robust and use embeddings later, but not yet.
    """

    query_words = set(query.lower().split())
    docs = load_documents()

    scored_docs = []

    for doc in docs:
        content_words = set(doc["content"].lower().split())
        score = len(query_words & content_words)

        scored_docs.append((score, doc))

    #sort by score best -----> worst
    scored_docs.sort(key = lambda x: x[0], reverse = True)

    # keep top N Default: N=3
    top_docs = [d for score, d in scored_docs if score > 0][:limit]

    return top_docs
