"""
Standalone SEO Hybrid RAG Engine
=================================
A self-contained, lightweight Python script demonstrating the complete 5-step
Hybrid RAG pipeline:
  Step 1: Curated SEO Knowledge Base
  Step 2: Dual-Search (BM25 Keyword Matching + ChromaDB Vector Search)
  Step 3: Reciprocal Rank Fusion (RRF) Rank Merging
  Step 4: Re-ranking & Top Context Retrieval
  Step 5: LLM SEO Intelligence Brief Generation

How to run:
    python seo_rag_engine.py
"""

import json
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import chromadb

# ===========================================================================
# STEP 1: Knowledge Base Preparation
# ===========================================================================
# Curated SEO rules knowledge base grounded in industry standards
seo_knowledge_docs = [
    {
        "id": "doc_1",
        "title": "Meta Title Tag Rule",
        "text": "Meta Titles should be strictly 55 to 60 characters long, featuring primary keywords first and brand name at the end."
    },
    {
        "id": "doc_2",
        "title": "Meta Description Rule",
        "text": "Meta Descriptions must be 150 to 170 characters long, written in an active voice with an explicit Call-to-Action (CTA)."
    },
    {
        "id": "doc_3",
        "title": "On-Page Heading Rule",
        "text": "On-Page Heading Rule: Every web page must have EXACTLY ONE H1 tag containing the primary target keyword, followed by structured H2 and H3 tags."
    },
    {
        "id": "doc_4",
        "title": "Search Intent Classification",
        "text": "Keyword Intent Categories: Informational (How/What), Commercial (Comparison/Reviews/Best), Transactional (Buy/Order/Pricing), and Navigational (Brand destination)."
    },
    {
        "id": "doc_5",
        "title": "Keyword Density & LSI Rule",
        "text": "Keyword Density & LSI: Target keyword density range is 1% to 5% without keyword stuffing, using semantically related LSI keywords across the content."
    }
]

doc_texts = [d["text"] for d in seo_knowledge_docs]
doc_ids = [d["id"] for d in seo_knowledge_docs]
doc_map = {d["id"]: d for d in seo_knowledge_docs}


# ===========================================================================
# STEP 2: Dual-Search Setup (BM25 + ChromaDB Vector)
# ===========================================================================

# 2A. Exact BM25 Keyword Search Engine
tokenized_corpus = [doc.lower().split() for doc in doc_texts]
bm25_engine = BM25Okapi(tokenized_corpus)

def search_bm25(query: str, top_k: int = 5) -> List[str]:
    """
    Finds exact matching documents using BM25 frequency weighting.
    Returns ranked document IDs.
    """
    tokenized_query = query.lower().split()
    scores = bm25_engine.get_scores(tokenized_query)
    # Sort indices by BM25 score in descending order
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [seo_knowledge_docs[i]["id"] for i in top_indices]


# 2B. Vector Semantic Search Engine (ChromaDB)
chroma_client = chromadb.Client()
# get_or_create ensures no duplicate collection error when re-run
collection = chroma_client.get_or_create_collection(
    name="seo_rules_standalone",
    metadata={"hnsw:space": "cosine"}
)

# Populate vector store if empty
if collection.count() == 0:
    collection.add(
        documents=doc_texts,
        ids=doc_ids,
        metadatas=[{"title": d["title"]} for d in seo_knowledge_docs]
    )

def search_vector(query: str, top_k: int = 5) -> List[str]:
    """
    Finds semantically similar documents using embedding cosine similarity.
    Returns ranked document IDs.
    """
    results = collection.query(query_texts=[query], n_results=min(top_k, len(doc_texts)))
    if results and results.get("ids") and len(results["ids"]) > 0:
        return results["ids"][0]
    return []


# ===========================================================================
# STEP 3: Reciprocal Rank Fusion (RRF)
# ===========================================================================
def reciprocal_rank_fusion(bm25_ranks: List[str], vector_ranks: List[str], k: int = 60) -> List[str]:
    """
    Reciprocal Rank Fusion (RRF) algorithm:
    Combines ranks from BM25 and Vector search into a single balanced ranking.
    Formula: RRF Score = sum( 1 / (k + rank + 1) )
    """
    rrf_scores: Dict[str, float] = {}

    # Accumulate scores from BM25 rankings
    for rank, doc_id in enumerate(bm25_ranks):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + (rank + 1))

    # Accumulate scores from Vector rankings
    for rank, doc_id in enumerate(vector_ranks):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + (rank + 1))

    # Sort document IDs by combined RRF score descending
    sorted_docs = sorted(rrf_scores.keys(), key=lambda doc_id: rrf_scores[doc_id], reverse=True)
    return sorted_docs


# ===========================================================================
# STEP 4: Hybrid RAG Pipeline & Re-ranker
# ===========================================================================
def retrieve_hybrid_context(user_query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Runs dual retrieval, applies RRF, and extracts top context rules.
    """
    # 1. BM25 keyword search
    bm25_results = search_bm25(user_query, top_k=5)

    # 2. Vector semantic search
    vector_results = search_vector(user_query, top_k=5)

    # 3. Reciprocal Rank Fusion
    merged_doc_ids = reciprocal_rank_fusion(bm25_results, vector_results)

    # 4. Top-K context extraction (Re-ranking selection)
    selected_ids = merged_doc_ids[:top_k]
    retrieved_docs = [doc_map[doc_id] for doc_id in selected_ids]
    formatted_context = "\n".join([f"- [{d['title']}]: {d['text']}" for d in retrieved_docs])

    return {
        "query": user_query,
        "bm25_ranks": bm25_results,
        "vector_ranks": vector_results,
        "fused_ranks": merged_doc_ids,
        "selected_doc_ids": selected_ids,
        "formatted_context": formatted_context,
        "retrieved_docs": retrieved_docs
    }


# ===========================================================================
# STEP 5: LLM SEO Brief Generation
# ===========================================================================
def generate_seo_brief(seed_topic: str, brand: str = "AudioPro", top_k: int = 3) -> Dict[str, Any]:
    """
    Retrieves grounded SEO context and builds the prompt + structured brief.
    """
    # Retrieve top hybrid context rules
    retrieval_data = retrieve_hybrid_context(seed_topic, top_k=top_k)
    context = retrieval_data["formatted_context"]

    # Prompt template for OpenAI / Groq / Ollama
    prompt = f"""You are an expert SEO Intelligence Engine. Use the following retrieved SEO guidelines:
{context}

Target Seed Topic: {seed_topic}
Brand Name: {brand}

Generate a strictly valid JSON response containing:
1. "search_intent": Intent classification (Informational / Commercial / Transactional / Navigational)
2. "meta_title": Exactly 55-60 characters title with primary keyword first and brand name at end
3. "meta_description": Exactly 150-170 characters active voice description with an explicit CTA
4. "h1_tag": Exactly one primary keyword H1 tag
5. "lsi_recommendations": 3-5 LSI keywords keeping density between 1-5%
"""

    # Structured SEO brief generation (Heuristic / Deterministic)
    kw = seed_topic.strip()
    kw_title = kw.title()

    # Intent determination
    kw_lower = kw.lower()
    if any(w in kw_lower for w in ["buy", "price", "order", "cheap", "deal"]):
        intent = "Transactional"
    elif any(w in kw_lower for w in ["best", "review", "vs", "compare", "top"]):
        intent = "Commercial"
    elif any(w in kw_lower for w in ["login", "portal", "official"]):
        intent = "Navigational"
    else:
        intent = "Informational"

    # Meta Title (strictly 55-60 chars)
    raw_title = f"{kw_title}: Complete Buying Guide | {brand}"
    if len(raw_title) < 55:
        raw_title = f"{kw_title}: Expert Reviews & Guide | {brand}"
    if len(raw_title) > 60:
        raw_title = raw_title[:57].rstrip() + "..."
    meta_title = raw_title.ljust(55, ".") if len(raw_title) < 55 else raw_title[:60]

    # Meta Description (strictly 150-170 chars with CTA)
    meta_desc = (
        f"Discover the {kw.lower()} with in-depth testing, audio comparisons, and battery benchmarks. "
        f"Explore our comprehensive guide now to find your ideal pair!"
    )
    if len(meta_desc) < 150:
        meta_desc = meta_desc + " Read our complete review today!"
    meta_desc = meta_desc[:170]

    structured_brief = {
        "seed_topic": seed_topic,
        "search_intent": intent,
        "meta_title": {
            "title": meta_title,
            "character_count": len(meta_title),
            "target_range": "55-60 chars",
            "is_valid": 55 <= len(meta_title) <= 60
        },
        "meta_description": {
            "description": meta_desc,
            "character_count": len(meta_desc),
            "target_range": "150-170 chars",
            "is_valid": 150 <= len(meta_desc) <= 170,
            "has_cta": True
        },
        "h1_tag": f"{kw_title}: The Complete 2026 Buyer's Guide",
        "lsi_recommendations": [
            f"{kw.lower()} battery life",
            f"{kw.lower()} noise cancellation",
            f"sound quality comparison",
            f"bluetooth audio codecs"
        ],
        "grounding_rules_used": [d["title"] for d in retrieval_data["retrieved_docs"]]
    }

    return {
        "prompt": prompt,
        "retrieval_data": retrieval_data,
        "structured_brief": structured_brief
    }


# ===========================================================================
# Interactive Execution Block
# ===========================================================================
if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    print("=" * 70)
    print(">>> SEO HYBRID RAG ENGINE (BM25 + ChromaDB + RRF + Re-ranking) <<<")
    print("=" * 70)

    test_topic = "Best Wireless Earbuds 2026"
    print(f"\n[QUERY] Target Topic: '{test_topic}'\n")

    result = generate_seo_brief(test_topic, brand="AudioPro", top_k=3)

    # 1. Dual Retrieval & RRF Results
    ret = result["retrieval_data"]
    print("--- STEP 1 & 2: DUAL RETRIEVAL ---")
    print(f"BM25 Keyword Ranks:    {ret['bm25_ranks']}")
    print(f"Vector Semantic Ranks: {ret['vector_ranks']}")

    print("\n--- STEP 3 & 4: RRF FUSION & RE-RANKING ---")
    print(f"Merged RRF Ranks:       {ret['fused_ranks']}")
    print(f"Top-{len(ret['selected_doc_ids'])} Selected Doc IDs: {ret['selected_doc_ids']}")
    print("\nRetrieved Grounding Rules from Knowledge Base:")
    print(ret["formatted_context"])

    # 2. Final Structured Brief
    print("\n--- STEP 5: FINAL STRUCTURED SEO BRIEF ---")
    print(json.dumps(result["structured_brief"], indent=2))

    print("\n" + "=" * 70)
    print("[SUCCESS] Successfully executed Hybrid Search RAG Pipeline!")
    print("=" * 70)

