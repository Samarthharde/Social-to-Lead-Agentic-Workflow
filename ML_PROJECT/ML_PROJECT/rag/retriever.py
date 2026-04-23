"""
RAG (Retrieval-Augmented Generation) pipeline for AutoStream knowledge base.
Uses a simple TF-IDF based retriever over the local Markdown knowledge base.
Falls back gracefully if scikit-learn is unavailable.
"""

import os
import re
from pathlib import Path
from typing import List


KB_PATH = Path(__file__).parent.parent / "knowledge_base" / "autostream_kb.md"


def _load_and_chunk_kb(path: Path) -> List[str]:
    """Load the knowledge base and split it into meaningful chunks."""
    text = path.read_text(encoding="utf-8")

    # Split on markdown headers (## or ###) to create semantic chunks
    chunks = re.split(r"\n(?=#{1,3} )", text)
    chunks = [c.strip() for c in chunks if c.strip()]
    return chunks


# Load chunks once at module import
_CHUNKS: List[str] = _load_and_chunk_kb(KB_PATH)


def retrieve(query: str, top_k: int = 3) -> str:
    """
    Retrieve the most relevant chunks from the knowledge base for a given query.

    Args:
        query: The user's question or search string
        top_k: Number of top chunks to return

    Returns:
        A single string containing the concatenated relevant chunks
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        corpus = _CHUNKS + [query]
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(corpus)

        query_vec = tfidf_matrix[-1]
        doc_vecs = tfidf_matrix[:-1]

        scores = cosine_similarity(query_vec, doc_vecs).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]

        relevant = [_CHUNKS[i] for i in top_indices if scores[i] > 0]
        if not relevant:
            # Fall back to returning the full KB if nothing matches
            relevant = _CHUNKS[:top_k]

    except ImportError:
        # Fallback: simple keyword matching
        query_lower = query.lower()
        keywords = query_lower.split()
        scored = []
        for chunk in _CHUNKS:
            chunk_lower = chunk.lower()
            score = sum(1 for kw in keywords if kw in chunk_lower)
            scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        relevant = [c for _, c in scored[:top_k] if _ > 0] or _CHUNKS[:top_k]

    return "\n\n---\n\n".join(relevant)


def get_full_kb() -> str:
    """Return the entire knowledge base as a string (used for system prompt seeding)."""
    return KB_PATH.read_text(encoding="utf-8")
