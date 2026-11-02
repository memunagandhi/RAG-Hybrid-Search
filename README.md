# ⚡ AI-Powered SEO Keyword & Content Intelligence Tool

An enterprise-grade, dark-themed **SEO Keyword & Content Intelligence Engine** powered by **Python**, **Streamlit**, and a **Hybrid Search RAG Pipeline** (BM25 keyword matching + ChromaDB vector embeddings + 6-line Reciprocal Rank Fusion + Cosine Re-ranking).

Grounded on a **curated local knowledge base of 25 SEO best practices**, this tool synthesizes structured search briefs, validates metadata, enforces single-H1 heading hierarchies, and monitors keyword density in real-time.

---

## 🌟 Key Features

- **Hybrid Search Retrieval**:
  - **BM25 Exact Keyword Matching**: Powered by `rank_bm25` for high-precision exact term overlap.
  - **Semantic Vector Search**: Powered by `chromadb` using `all-MiniLM-L6-v2` dense embeddings.
  - **6-Line Reciprocal Rank Fusion (RRF)**: Merges keyword and vector rankings using the standard RRF formula:
    $$\text{RRF Score}(d) = \sum_{r \in \text{retrievers}} \frac{1}{k + \text{rank}(d) + 1}$$
  - **Re-Ranking**: Computes cosine similarity against the query embedding to select the most relevant SEO best practices.
- **Local Knowledge Base**: 25 pre-indexed SEO best practices spanning On-Page SEO, Keyword Strategy, Off-Page SEO, Technical SEO, Content Strategy, Local SEO, and Analytics.
- **SEO Processing Module**:
  - Multi-provider support: **OpenAI** (`gpt-4o-mini`, `gpt-4o`), **Groq** (`llama-3.3-70b-versatile`, `mixtral-8x7b`), **Ollama** (`llama3`), and an instant **Mock Engine** (0 API keys required).
  - Strict constraint enforcement:
    1. **Intent Classification**: Informational, Commercial, Transactional, Navigational.
    2. **Meta Title Generator**: Strictly 55–60 characters, primary keyword placed first, brand name included.
    3. **Meta Description Generator**: Strictly 150–170 characters, active voice, explicit CTA.
    4. **Heading Tag Outline**: Enforces **EXACTLY ONE H1** containing the primary keyword, with structured H2/H3 subheadings.
    5. **LSI Keywords & Density Analysis**: Target 1.0% – 5.0% range; triggers **Keyword Stuffing** warning if density exceeds 5.0%.
- **Dark-Themed Streamlit Dashboard**:
  - **Google SERP Dark Mode Mockup**: Realistic live search snippet preview.
  - **Live Content Editor**: Real-time keyword density calculation as you type.
  - **1-Click Actions**: "Copy All" popover and "Export Markdown" `.md` download.

---

## 📁 Repository Structure

```
.
├── .streamlit/
│   └── config.toml           # Dark theme configuration
├── app.py                    # Streamlit Dashboard UI
├── hybrid_search.py          # BM25 + ChromaDB + 6-Line RRF + Re-ranking
├── seo_processor.py          # Multi-LLM SEO processing module & validators
├── seo_knowledge_base.py     # Local database of 25 curated SEO best practices
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation and deployment guide
```

---

## ⚡ 6-Line Reciprocal Rank Fusion (RRF) Function

Defined in [`hybrid_search.py`](hybrid_search.py):

```python
def reciprocal_rank_fusion(bm25_ranks: list, vector_ranks: list, k: int = 60) -> list:
    rrf_scores = {}
    for rank, (doc_id, _) in enumerate(bm25_ranks):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    for rank, (doc_id, _) in enumerate(vector_ranks):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
```

---

## 💻 How to Run Locally

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- Git installed.

### Step 1: Clone or Navigate to the Project Directory

```bash
cd "RAG Hybrid Search"
```

### Step 2: Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Streamlit Application

```bash
streamlit run app.py
```

The application will open in your default browser at:
```
http://localhost:8501
```

> **Tip:** You can start using the application immediately with the **Mock Engine** without any API key, or choose **OpenAI / Groq / Ollama** in the sidebar.

---

## ☁️ How to Deploy on Streamlit Community Cloud for Free Today

Streamlit Community Cloud lets you deploy and share Python apps for free directly from GitHub.

### Step 1: Push Your Project to GitHub

1. Create a new repository on [GitHub](https://github.com/new) (e.g. `seo-content-intelligence`).
2. Initialize and push your local directory to GitHub:

```bash
git init
git add .
git commit -m "Initial commit: AI-Powered SEO Keyword & Content Intelligence Tool"
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git
git push -u origin main
```

### Step 2: Sign In to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Click **"Continue with GitHub"** to sign in.

### Step 3: Create a New App

1. Click the **"Create app"** or **"New app"** button.
2. Select **"Deploy a public app from GitHub"**.
3. Fill in the repository details:
   - **Repository:** `<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL (optional):** Choose a custom subdomain (e.g., `my-seo-intelligence.streamlit.app`).

### Step 4: (Optional) Configure API Secrets

If you want default API keys for OpenAI or Groq automatically loaded in the cloud without typing them into the UI:

1. In the deployment screen, click **"Advanced settings..."**.
2. Under **"Secrets"**, add your keys in TOML format:
   ```toml
   OPENAI_API_KEY = "sk-..."
   GROQ_API_KEY = "gsk_..."
   ```
3. Click **"Save"**.

### Step 5: Deploy!

1. Click **"Deploy!"**.
2. Streamlit Cloud will automatically provision a container, install packages from `requirements.txt`, and start the app.
3. Within 1 to 2 minutes, your application is live on the internet with a public link you can share with anyone!

---

## 📦 Output Format: Structured JSON

When executing through the API or headless pipelines, the tool returns structured JSON:

```json
{
  "seed_keyword": "hybrid search rag",
  "intent_classification": {
    "intent": "Informational",
    "confidence_score": 0.95,
    "reasoning": "The query seeks technical architectural best practices."
  },
  "meta_title": {
    "title": "Hybrid Search Rag: Complete Architecture Guide | RankMaster",
    "character_count": 59,
    "is_valid_length": true,
    "has_primary_keyword_first": true,
    "brand_name": "RankMaster"
  },
  "meta_description": {
    "description": "Master hybrid search rag with BM25, vector embeddings, and reciprocal rank fusion. Read our expert step-by-step guide now to boost your AI retrieval precision!",
    "character_count": 161,
    "is_valid_length": true,
    "has_active_voice": true,
    "explicit_cta": "Read our expert step-by-step guide now!"
  },
  "heading_tag_outline": {
    "h1": "Hybrid Search Rag: Complete Architecture and Best Practices",
    "h2_sections": [
      {
        "h2": "Understanding Hybrid Search Rag and Search Intent",
        "lsi_keywords_used": ["search intent for hybrid search rag"],
        "h3_subsections": [
          "Why Hybrid Search Rag Matters for Retrieval Accuracy",
          "BM25 vs Vector Embeddings: Core Differences"
        ]
      }
    ]
  },
  "lsi_keywords": [
    "hybrid search rag best practices",
    "reciprocal rank fusion python",
    "bm25 and chromadb hybrid",
    "reranking search results"
  ],
  "sample_content": "...",
  "keyword_density_analysis": {
    "total_words": 142,
    "overall_status": "OPTIMAL",
    "keywords": {
      "hybrid search rag": {
        "occurrences": 3,
        "density_percent": 2.11,
        "status": "OPTIMAL",
        "is_stuffing": false,
        "in_target_range": true
      }
    }
  }
}
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

