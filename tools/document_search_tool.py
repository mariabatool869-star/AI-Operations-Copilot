"""
Tool: search_maintenance_logs

TWO SEARCH METHODS, EXPLAINED SIMPLY:

1. TF-IDF + cosine similarity (used in THIS environment, works offline):
   TF-IDF turns each sentence into a list of numbers based on which words
   appear and how rare/important those words are across all documents.
   "Cosine similarity" is just a way of measuring how close two lists of
   numbers point in the same direction - the closer, the more similar the
   text. This catches some shared-word and related-word patterns, but it
   is still fundamentally counting words, not truly understanding meaning.

2. Real sentence-embedding model (sentence-transformers) - the upgrade
   path for running this on your own machine, where a small pretrained AI
   model can be downloaded. This model was trained on millions of real
   sentences to genuinely learn which sentences mean similar things, even
   with completely different words. The code below tries this first, and
   only falls back to TF-IDF if the model can't be downloaded (like in
   this sandboxed environment).
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from data.maintenance_logs import MAINTENANCE_LOGS

_DOCS = [log["text"] for log in MAINTENANCE_LOGS]

_embedding_model = None
try:
    from sentence_transformers import SentenceTransformer
    _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    _doc_embeddings = _embedding_model.encode(_DOCS)
    print("Using real sentence-embedding model (all-MiniLM-L6-v2)")
except Exception as e:
    print(f"Real embedding model unavailable ({type(e).__name__}), using TF-IDF fallback")
    _embedding_model = None
    _vectorizer = TfidfVectorizer(stop_words="english")
    _doc_vectors = _vectorizer.fit_transform(_DOCS)


def search_maintenance_logs(query: str, top_k: int = 3) -> dict:
    """
    Searches maintenance logs by MEANING, not exact keyword match.
    Returns the top_k most similar log entries with a similarity score.
    """
    if _embedding_model is not None:
        query_embedding = _embedding_model.encode([query])
        scores = cosine_similarity(query_embedding, _doc_embeddings)[0]
        method = "sentence-embedding model (all-MiniLM-L6-v2)"
    else:
        query_vector = _vectorizer.transform([query])
        scores = cosine_similarity(query_vector, _doc_vectors)[0]
        method = "TF-IDF (word-frequency based, fallback method)"

    top_indices = np.argsort(scores)[::-1][:top_k]
    results = [
        {
            "log_id": MAINTENANCE_LOGS[i]["id"],
            "asset_id": MAINTENANCE_LOGS[i]["asset_id"],
            "text": MAINTENANCE_LOGS[i]["text"],
            "similarity_score": round(float(scores[i]), 3),
        }
        for i in top_indices if scores[i] > 0
    ]

    return {"query": query, "search_method": method, "results": results}


if __name__ == "__main__":
    print("\nQuery: 'any leak issues on compressors?' (note: no log uses the word 'leak')")
    result = search_maintenance_logs("any leak issues on compressors?")
    for r in result["results"]:
        print(f"  [{r['similarity_score']}] {r['log_id']} ({r['asset_id']}): {r['text']}")

    print("\nQuery: 'corrosion on tanks'")
    result2 = search_maintenance_logs("corrosion on tanks")
    for r in result2["results"]:
        print(f"  [{r['similarity_score']}] {r['log_id']} ({r['asset_id']}): {r['text']}")
