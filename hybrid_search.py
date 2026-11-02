"""
Hybrid Search Engine: BM25 (keyword) + ChromaDB/Vector (semantic) with Reciprocal Rank Fusion.
Combines exact keyword matching with semantic vector search, followed by 6-line RRF and re-ranking.
"""

import math
import numpy as np
from typing import List, Tuple, Dict, Any

from seo_knowledge_base import SEO_KNOWLEDGE_BASE

# ---------------------------------------------------------------------------
# Globals – initialized lazily via setup()
# ---------------------------------------------------------------------------
_bm25 = None
_collection = None
_embedder = None
_vector_fallback_embeddings = None
_corpus_tokens: List[List[str]] = []
_doc_ids: List[str] = []
_using_chroma = False


def _tokenize(text: str) -> List[str]:
    """Whitespace and lowercase tokenizer with basic punctuation stripping."""
    import re
    return re.findall(r'\b[a-zA-Z0-9_\-]+\b', text.lower())


def _doc_text(doc: dict) -> str:
    """Concatenate title, category, and content into one searchable string."""
    return f"{doc['title']} {doc['category']} {doc['content']}"


# ---------------------------------------------------------------------------
# Setup: build BM25 index & Vector Store (ChromaDB or Lightweight Vector)
# ---------------------------------------------------------------------------

class LightweightBM25:
    """Standard Okapi BM25 implementation for zero-dependency keyword matching."""
    def __init__(self, corpus: List[List[str]], k1: float = 1.5, b: float = 0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.doc_len = [len(doc) for doc in corpus]
        self.avg_doc_len = sum(self.doc_len) / max(len(corpus), 1)
        self.df = {}
        for doc in corpus:
            for term in set(doc):
                self.df[term] = self.df.get(term, 0) + 1
        self.idf = {
            term: math.log((len(corpus) - count + 0.5) / (count + 0.5) + 1.0)
            for term, count in self.df.items()
        }

    def get_scores(self, query_tokens: List[str]) -> List[float]:
        scores = [0.0] * len(self.corpus)
        for term in query_tokens:
            if term not in self.idf:
                continue
            idf_val = self.idf[term]
            for idx, doc in enumerate(self.corpus):
                freq = doc.count(term)
                if freq > 0:
                    numerator = freq * (self.k1 + 1)
                    denominator = freq + self.k1 * (1 - self.b + self.b * (self.doc_len[idx] / self.avg_doc_len))
                    scores[idx] += idf_val * (numerator / denominator)
        return scores


def setup():
    """Initialise BM25 index and vector search engine (idempotent)."""
    global _bm25, _collection, _embedder, _vector_fallback_embeddings, _corpus_tokens, _doc_ids, _using_chroma

    if _bm25 is not None:
        return  # already initialized

    _corpus_tokens = [_tokenize(_doc_text(d)) for d in SEO_KNOWLEDGE_BASE]
    _doc_ids = [d["id"] for d in SEO_KNOWLEDGE_BASE]

    # Initialize BM25
    try:
        from rank_bm25 import BM25Okapi
        _bm25 = BM25Okapi(_corpus_tokens)
    except ImportError:
        _bm25 = LightweightBM25(_corpus_tokens)

    # Initialize Vector Store (ChromaDB + SentenceTransformers or TF-IDF Vector Space)
    texts = [_doc_text(d) for d in SEO_KNOWLEDGE_BASE]
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        client = chromadb.Client()
        _collection = client.get_or_create_collection(
            name="seo_kb_hybrid",
            metadata={"hnsw:space": "cosine"}
        )
        if _collection.count() == 0:
            embeddings = _embedder.encode(texts).tolist()
            _collection.add(
                ids=_doc_ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=[{"title": d["title"], "category": d["category"]} for d in SEO_KNOWLEDGE_BASE]
            )
        _using_chroma = True
    except Exception:
        # High quality TF-IDF dense vector space fallback
        _using_chroma = False
        vocab = sorted({w for doc in _corpus_tokens for w in doc})
        vocab_map = {w: i for i, w in enumerate(vocab)}
        doc_vectors = []
        for doc in _corpus_tokens:
            vec = np.zeros(len(vocab), dtype=np.float32)
            for w in doc:
                vec[vocab_map[w]] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            doc_vectors.append(vec)
        _vector_fallback_embeddings = (vocab_map, np.array(doc_vectors))


# ---------------------------------------------------------------------------
# Individual Retrievers
# ---------------------------------------------------------------------------

def bm25_search(query: str, top_k: int = 10) -> List[Tuple[str, float]]:
    """Return ranked list of (doc_id, score) using BM25 keyword matching."""
    scores = _bm25.get_scores(_tokenize(query))
    ranked = sorted(zip(_doc_ids, scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


def vector_search(query: str, top_k: int = 10) -> List[Tuple[str, float]]:
    """Return ranked list of (doc_id, score/distance) using semantic vector search."""
    if _using_chroma and _collection is not None and _embedder is not None:
        query_emb = _embedder.encode([query]).tolist()
        results = _collection.query(query_embeddings=query_emb, n_results=top_k)
        ids = results["ids"][0]
        distances = results["distances"][0]
        return list(zip(ids, distances))
    else:
        # Vector fallback cosine similarity
        vocab_map, doc_mat = _vector_fallback_embeddings
        q_vec = np.zeros(len(vocab_map), dtype=np.float32)
        for w in _tokenize(query):
            if w in vocab_map:
                q_vec[vocab_map[w]] += 1.0
        norm = np.linalg.norm(q_vec)
        if norm > 0:
            q_vec = q_vec / norm
        sims = np.dot(doc_mat, q_vec)
        ranked = sorted(zip(_doc_ids, sims), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion (RRF) — Strictly 6 Lines
# ---------------------------------------------------------------------------

def reciprocal_rank_fusion(bm25_ranks: list, vector_ranks: list, k: int = 60) -> list:
    rrf_scores = {}
    for rank, (doc_id, _) in enumerate(bm25_ranks):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    for rank, (doc_id, _) in enumerate(vector_ranks):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)


# ---------------------------------------------------------------------------
# Re-ranking: Cosine Similarity Scoring
# ---------------------------------------------------------------------------

def rerank(query: str, fused_results: List[Tuple[str, float]], top_n: int = 5) -> List[Dict[str, Any]]:
    """Re-rank fused candidates by computing semantic relevance to the query."""
    doc_map = {d["id"]: d for d in SEO_KNOWLEDGE_BASE}
    scored = []

    if _using_chroma and _embedder is not None:
        query_emb = _embedder.encode([query])[0]
        for doc_id, rrf_score in fused_results:
            doc = doc_map[doc_id]
            doc_emb = _embedder.encode([_doc_text(doc)])[0]
            sim = float(np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb) + 1e-9))
            scored.append({
                "id": doc_id,
                "title": doc["title"],
                "category": doc["category"],
                "content": doc["content"],
                "rrf_score": round(rrf_score, 6),
                "rerank_score": round(sim, 4),
            })
    else:
        # Fallback cosine calculation
        vocab_map, doc_mat = _vector_fallback_embeddings
        id_to_idx = {doc_id: i for i, doc_id in enumerate(_doc_ids)}
        q_vec = np.zeros(len(vocab_map), dtype=np.float32)
        for w in _tokenize(query):
            if w in vocab_map:
                q_vec[vocab_map[w]] += 1.0
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        for doc_id, rrf_score in fused_results:
            doc = doc_map[doc_id]
            idx = id_to_idx[doc_id]
            doc_v = doc_mat[idx]
            sim = float(np.dot(doc_v, q_vec))
            scored.append({
                "id": doc_id,
                "title": doc["title"],
                "category": doc["category"],
                "content": doc["content"],
                "rrf_score": round(rrf_score, 6),
                "rerank_score": round(sim, 4),
            })

    scored.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored[:top_n]


# ---------------------------------------------------------------------------
# Public High-Level API
# ---------------------------------------------------------------------------

def hybrid_search(query: str, top_k: int = 10, top_n: int = 5, k_rrf: int = 60) -> Dict[str, Any]:
    """Run full hybrid search pipeline (BM25 + Vector -> RRF -> Re-ranking)."""
    setup()

    bm25_results = bm25_search(query, top_k)
    vec_results = vector_search(query, top_k)
    fused = reciprocal_rank_fusion(bm25_results, vec_results, k=k_rrf)
    reranked = rerank(query, fused, top_n)

    return {
        "query": query,
        "bm25_results": bm25_results,
        "vector_results": vec_results,
        "fused_results": fused,
        "reranked_results": reranked,
        "backend": "ChromaDB" if _using_chroma else "Vector Engine (Fallback)"
    }
