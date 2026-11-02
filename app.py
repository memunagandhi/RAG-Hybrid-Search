"""
AI-Powered SEO Keyword & Content Intelligence Tool
Professional Dark-Themed Streamlit Dashboard UI featuring:
- Hybrid Search (BM25 + ChromaDB + 6-Line RRF + Re-ranking)
- Local Knowledge Base Status & Document Browser
- SEO Processing Module (OpenAI, Groq, Ollama, Mock Engine)
- Tab 1: Search Intent & Overview
- Tab 2: Meta Tags & Title Preview (with Google SERP Dark Mode Mockup)
- Tab 3: On-Page H1-H6 Structure
- Tab 4: LSI Keywords & Density Analysis (Target 1-5% range, stuffing alert)
- 'Copy All' and 'Export Markdown' buttons
"""

import json
from datetime import datetime
import streamlit as st
import pandas as pd

from hybrid_search import hybrid_search, setup
from seo_knowledge_base import SEO_KNOWLEDGE_BASE
from seo_processor import (
    process_seo_keyword,
    calculate_keyword_density,
    generate_markdown_brief,
    enforce_meta_title,
    enforce_meta_description
)

# ---------------------------------------------------------------------------
# Streamlit App Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SEO Intelligence Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for Sleek Dark Theme UI
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Dark Theme Core Variables */
    :root {
        --bg-dark: #0b0f19;
        --surface-dark: #111827;
        --card-dark: #1e293b;
        --border-dark: #334155;
        --accent-indigo: #6366f1;
        --accent-violet: #8b5cf6;
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --accent-rose: #f43f5e;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }

    /* Main Container Styles */
    .stApp {
        background-color: var(--bg-dark);
        color: var(--text-primary);
    }

    /* Gradient Title */
    .hero-header {
        font-size: 2.25rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
        margin-bottom: 0.25rem;
    }

    .hero-sub {
        font-size: 0.95rem;
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
        font-weight: 400;
    }

    /* Dark Card Container */
    .dark-card {
        background: #151d30;
        border: 1px solid #24324d;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
    }

    .card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Status Pills and Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }

    .badge-info { background: rgba(6, 182, 212, 0.15); color: #38bdf8; border: 1px solid rgba(6, 182, 212, 0.3); }
    .badge-comm { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-trans { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-nav { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }

    .badge-success { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-warning { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-danger { background: rgba(244, 63, 94, 0.15); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); }
    .badge-muted { background: rgba(148, 163, 184, 0.1); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.2); }

    /* Google SERP Dark Mode Preview Mockup */
    .serp-box {
        background: #202124;
        border: 1px solid #3c4043;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-top: 0.75rem;
        font-family: Roboto, Arial, sans-serif;
    }

    .serp-url-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.35rem;
        font-size: 0.85rem;
        color: #dadce0;
    }

    .serp-favicon {
        width: 18px;
        height: 18px;
        background: #8ab4f8;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        color: #202124;
    }

    .serp-title {
        font-size: 1.25rem;
        line-height: 1.35;
        color: #8ab4f8;
        font-weight: 500;
        cursor: pointer;
        text-decoration: none;
        margin-bottom: 0.4rem;
    }

    .serp-title:hover {
        text-decoration: underline;
    }

    .serp-snippet {
        font-size: 0.92rem;
        color: #bdc1c6;
        line-height: 1.55;
    }

    /* Heading Tree Hierarchy */
    .heading-h1 {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.05) 100%);
        border-left: 4px solid #818cf8;
        padding: 0.85rem 1.15rem;
        border-radius: 8px;
        font-size: 1.05rem;
        font-weight: 700;
        color: #e0e7ff;
        margin-bottom: 0.85rem;
    }

    .heading-h2 {
        background: #131b2e;
        border-left: 4px solid #06b6d4;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        font-size: 0.95rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.4rem;
        margin-top: 0.6rem;
    }

    .heading-h3 {
        background: #0f172a;
        border-left: 3px solid #64748b;
        padding: 0.45rem 0.85rem;
        border-radius: 4px;
        font-size: 0.88rem;
        color: #94a3b8;
        margin-left: 1.5rem;
        margin-bottom: 0.3rem;
    }

    /* Metric Ribbons */
    .metric-strip {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 0.75rem;
        margin-bottom: 1.25rem;
    }

    .stat-box {
        background: #151d30;
        border: 1px solid #24324d;
        border-radius: 10px;
        padding: 0.85rem 0.75rem;
        text-align: center;
    }

    .stat-value {
        font-size: 1.35rem;
        font-weight: 800;
        color: #f8fafc;
    }

    .stat-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.04em;
        margin-top: 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Lazy Setup Engine
# ---------------------------------------------------------------------------
if "engine_ready" not in st.session_state:
    with st.spinner("⚡ Initializing Hybrid Search Engine (BM25 + ChromaDB)..."):
        setup()
        st.session_state["engine_ready"] = True


# ===========================================================================
# SIDEBAR: API Key, Model Selection, Knowledge Base Status
# ===========================================================================
with st.sidebar:
    st.markdown("### ⚙️ Engine Configuration")

    # 1. API Provider & Model Selection
    llm_provider = st.selectbox(
        "LLM Provider",
        ["Mock Engine (Instant / Offline)", "Groq API", "OpenAI API", "Ollama (Local LLM)"],
        index=0,
        help="Mock Engine works instantly with 0 keys. Use Groq/OpenAI for live LLM API generation."
    )

    api_key = ""
    model_name = ""
    ollama_url = "http://localhost:11434"

    if llm_provider == "Groq API":
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        model_name = st.selectbox(
            "Groq Model",
            ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            index=0
        )
    elif llm_provider == "OpenAI API":
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        model_name = st.selectbox(
            "OpenAI Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0
        )
    elif llm_provider == "Ollama (Local LLM)":
        ollama_url = st.text_input("Ollama Base URL", value="http://localhost:11434")
        model_name = st.text_input("Model Name", value="llama3")

    brand_name = st.text_input("Brand / Site Name", value="RankMaster", placeholder="e.g. SEOPro, TechRadar")

    st.divider()

    # 2. Knowledge Base Status
    st.markdown("### 📚 Knowledge Base Status")
    
    kb_col1, kb_col2 = st.columns(2)
    with kb_col1:
        st.markdown(
            """
            <div class="stat-box">
                <div class="stat-value" style="color:#34d399;">🟢 ACTIVE</div>
                <div class="stat-label">Hybrid RAG</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with kb_col2:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-value">{len(SEO_KNOWLEDGE_BASE)}</div>
                <div class="stat-label">Indexed Docs</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    categories = sorted({d["category"] for d in SEO_KNOWLEDGE_BASE})
    st.caption(f"**Indexed SEO Domains ({len(categories)}):** " + ", ".join(categories))

    with st.expander("🔍 Inspect Knowledge Base Best Practices"):
        cat_filter = st.selectbox("Filter Category", ["All"] + categories)
        docs_to_show = SEO_KNOWLEDGE_BASE if cat_filter == "All" else [d for d in SEO_KNOWLEDGE_BASE if d["category"] == cat_filter]
        for d in docs_to_show:
            st.markdown(f"**[{d['category']}] {d['title']}**")
            st.caption(d["content"])
            st.markdown("---")

    st.divider()

    # 3. Hybrid Search Tuning
    st.markdown("### 🎛️ Hybrid Search Parameters")
    top_k = st.slider("Candidates per Retriever (top-k)", 5, 25, 10)
    top_n = st.slider("Context Documents for Prompt (top-n)", 1, 10, 3)
    rrf_k = st.slider("RRF Constant (k)", 1, 100, 60, help="Standard smoothing constant k=60.")


# ===========================================================================
# MAIN AREA: Header, Search Bar & Generate Button
# ===========================================================================
st.markdown('<div class="hero-header">⚡ AI SEO Keyword & Content Intelligence Tool</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">'
    'Hybrid Search Retrieval (BM25 + ChromaDB + 6-Line RRF + Re-ranking) '
    'grounded on curated SEO best practices.'
    '</div>',
    unsafe_allow_html=True
)

# Search Bar Row
search_col, btn_col = st.columns([4, 1.3])
with search_col:
    seed_input = st.text_input(
        "Target Seed Keyword / Topic",
        value="hybrid search rag",
        placeholder="Enter keyword or topic (e.g., technical seo audit, core web vitals lcp, best running shoes)...",
        label_visibility="collapsed"
    )
with btn_col:
    generate_btn = st.button("🚀 Generate SEO Brief", type="primary", use_container_width=True)

# Keyword Preset Chips
st.markdown("**💡 Quick Keyword Presets:**")
preset_cols = st.columns(4)
presets = [
    "hybrid search rag",
    "technical seo audit",
    "best running shoes for flat feet",
    "core web vitals optimization"
]
for i, p in enumerate(presets):
    if preset_cols[i].button(f"📌 {p}", key=f"preset_{i}", use_container_width=True):
        seed_input = p
        st.rerun()


# ===========================================================================
# GENERATION LOGIC & SESSION CACHING
# ===========================================================================
if generate_btn:
    with st.spinner("🔍 1. Running Hybrid Search (BM25 + ChromaDB + 6-line RRF + Re-ranking)..."):
        rag_data = hybrid_search(seed_input, top_k=top_k, top_n=top_n, k_rrf=rrf_k)
        rag_text = "\n".join([f"- {r['title']} ({r['category']}): {r['content']}" for r in rag_data["reranked_results"]])

    with st.spinner(f"🧠 2. Synthesizing SEO Intelligence via {llm_provider}..."):
        seo_res = process_seo_keyword(
            seed_keyword=seed_input,
            brand=brand_name,
            provider=llm_provider,
            api_key=api_key,
            model_name=model_name,
            ollama_url=ollama_url,
            rag_context=rag_text
        )
        st.session_state["seo_res"] = seo_res
        st.session_state["rag_data"] = rag_data


# ===========================================================================
# OUTPUT SECTION: Clean UI Cards & Tabs
# ===========================================================================
if "seo_res" in st.session_state:
    res = st.session_state["seo_res"]
    rag = st.session_state.get("rag_data", None)
    kw_title = res["seed_keyword"].title()
    brand_used = res["meta_title"].get("brand_name", brand_name)

    # If any fallback alert occurred
    if "api_warning" in res:
        st.warning(f"⚠️ {res['api_warning']}")

    st.markdown("---")

    # -----------------------------------------------------------------------
    # Top Action Bar: Copy All & Export Markdown + Metrics Strip
    # -----------------------------------------------------------------------
    action_col1, action_col2 = st.columns([3, 2])
    with action_col1:
        st.markdown(f"### 📋 SEO Intelligence Brief: <span style='color:#818cf8;'>{kw_title}</span>", unsafe_allow_html=True)
    with action_col2:
        markdown_content = generate_markdown_brief(res)
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            st.download_button(
                label="📥 Export Markdown",
                data=markdown_content,
                file_name=f"seo_brief_{res['seed_keyword'].replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with btn_c2:
            copy_popover = st.popover("📋 Copy All", use_container_width=True)
            with copy_popover:
                st.caption("Click the copy icon on the top-right of the code block:")
                st.code(markdown_content, language="markdown")

    # Quick Metrics Strip
    intent_val = res["intent_classification"].get("intent", "Informational")
    title_len = res["meta_title"].get("character_count", 0)
    desc_len = res["meta_description"].get("character_count", 0)
    density_stat = res["keyword_density_analysis"].get("overall_status", "OPTIMAL")

    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="stat-box">
                <div class="stat-value" style="color:#38bdf8;">{intent_val.upper()}</div>
                <div class="stat-label">Search Intent</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color:{'#10b981' if 55 <= title_len <= 60 else '#f59e0b'};">{title_len} / 60</div>
                <div class="stat-label">Title Length (55-60)</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color:{'#10b981' if 150 <= desc_len <= 170 else '#f59e0b'};">{desc_len} / 170</div>
                <div class="stat-label">Meta Desc (150-170)</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color:#c084fc;">1 H1 + {len(res['heading_tag_outline'].get('h2_sections', []))} H2s</div>
                <div class="stat-label">Heading Structure</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color:{'#f43f5e' if density_stat == 'FLAGGED_STUFFING' else '#10b981'};">
                    {'🚨 STUFFING' if density_stat == 'FLAGGED_STUFFING' else '✅ OPTIMAL'}
                </div>
                <div class="stat-label">Density Status</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------------------------
    # 4 Dedicated Tabs
    # -----------------------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Tab 1: Search Intent & Overview",
        "🌐 Tab 2: Meta Tags & Title Preview",
        "📑 Tab 3: On-Page H1-H6 Structure",
        "📊 Tab 4: LSI Keywords & Density Analysis"
    ])

    # =======================================================================
    # TAB 1: Search Intent & Overview
    # =======================================================================
    with tab1:
        intent_info = res["intent_classification"]
        intent_category = intent_info.get("intent", "Informational")
        confidence = int(intent_info.get("confidence_score", 0.95) * 100)
        reasoning = intent_info.get("reasoning", "")

        intent_badges = {
            "Informational": "badge-info",
            "Commercial": "badge-comm",
            "Transactional": "badge-trans",
            "Navigational": "badge-nav"
        }
        active_badge = intent_badges.get(intent_category, "badge-info")

        st.markdown(
            f"""
            <div class="dark-card">
                <div class="card-title">🎯 1. Keyword Intent Classification</div>
                <div style="margin-bottom:0.75rem;">
                    <span class="badge {active_badge}">🎯 {intent_category.upper()} INTENT</span>
                    <span class="badge badge-muted">Confidence Score: {confidence}%</span>
                    <span class="badge badge-muted">Target SERP: Top 1-5 Positions</span>
                </div>
                <p style="color:#cbd5e1; font-size:0.95rem; line-height:1.6; margin-bottom:0;">
                    <strong>Strategic Intent Rationale:</strong> {reasoning}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Overview & SERP Strategy Breakdown
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown(
                f"""
                <div class="dark-card">
                    <div class="card-title">📌 Content Strategy Recommendations</div>
                    <ul style="color:#cbd5e1; font-size:0.92rem; line-height:1.7; padding-left:1.2rem;">
                        <li><strong>Content Format:</strong> {'Comprehensive in-depth guide / tutorial' if intent_category == 'Informational' else ('Comparative review with pros/cons matrix' if intent_category == 'Commercial' else 'Optimized product landing page with direct CTA')}</li>
                        <li><strong>Target Word Count:</strong> 1,500 – 2,500 words for competitive SERP dominance.</li>
                        <li><strong>E-E-A-T Signals:</strong> Include verified author bio, original benchmark data, and authoritative outbound links.</li>
                        <li><strong>Internal Linking:</strong> Hub-and-spoke cluster links to relevant subtopics.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c_right:
            st.markdown(
                f"""
                <div class="dark-card">
                    <div class="card-title">🏆 Featured Snippet Opportunity</div>
                    <p style="color:#cbd5e1; font-size:0.92rem; line-height:1.6;">
                        Format the direct answer to <code>{res['seed_keyword']}</code> in a concise <strong>40-60 word definition paragraph</strong> 
                        under the first H2 tag to capture Position Zero.
                    </p>
                    <div style="background:#0f172a; padding:0.75rem 1rem; border-radius:6px; border:1px solid #1e293b; color:#38bdf8; font-size:0.85rem;">
                        💡 <strong>Pro Tip:</strong> Implement structured FAQ or HowTo schema JSON-LD markup to claim rich snippet enhancements.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Grounding Knowledge Base Context
        if rag:
            with st.expander(f"📚 Grounding Knowledge Base Context (Top {len(rag['reranked_results'])} Retrieved)"):
                for idx, r in enumerate(rag.get("reranked_results", []), 1):
                    st.markdown(f"**#{idx} {r['title']}** &nbsp; <span class='badge badge-muted'>{r['category']}</span>", unsafe_allow_html=True)
                    st.markdown(f"> *{r['content']}*")
                    st.caption(f"BM25 + ChromaDB RRF Score: {r['rrf_score']} | Re-rank Cosine Sim: {r['rerank_score']}")
                    st.markdown("---")

    # =======================================================================
    # TAB 2: Meta Tags & Title Preview (Google SERP Dark Mode Mockup)
    # =======================================================================
    with tab2:
        title_obj = res["meta_title"]
        desc_obj = res["meta_description"]
        title_text = title_obj.get("title", "")
        desc_text = desc_obj.get("description", "")
        slug = res["seed_keyword"].strip().lower().replace(" ", "-")

        # Google Search Dark Mode Snippet
        st.markdown(
            f"""
            <div class="dark-card">
                <div class="card-title">🔍 Live Google SERP Dark Mode Search Snippet Preview</div>
                <div class="serp-box">
                    <div class="serp-url-row">
                        <div class="serp-favicon">⚡</div>
                        <div>
                            <div>{brand_used}</div>
                            <div style="font-size:0.75rem; color:#9aa0a6;">https://www.{brand_used.lower().replace(' ', '')}.com › blog › {slug}</div>
                        </div>
                    </div>
                    <div class="serp-title">{title_text}</div>
                    <div class="serp-snippet">{desc_text}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            t_valid = title_obj.get("is_valid_length", False)
            t_badge = "badge-success" if t_valid else "badge-warning"
            st.markdown(
                f"""
                <div class="dark-card">
                    <div class="card-title">🏷️ Meta Title Specification</div>
                    <div style="margin-bottom:0.75rem;">
                        <span class="badge {t_badge}">{'✅ STRICT 55-60 CHARS' if t_valid else '⚠️ LENGTH OUTSIDE 55-60'} ({title_len} chars)</span>
                        <span class="badge badge-success">✅ Primary Keyword First</span>
                        <span class="badge badge-muted">Brand: {brand_used}</span>
                    </div>
                    <div style="background:#0b1120; border:1px solid #1e293b; border-radius:8px; padding:0.85rem 1rem; color:#e2e8f0; font-size:1.0rem; font-weight:600;">
                        {title_text}
                    </div>
                    <div style="margin-top:0.6rem; font-size:0.82rem; color:#94a3b8;">
                        Target range: 55 to 60 characters. Preserves mobile and desktop SERP title readability without truncation.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_m2:
            d_valid = desc_obj.get("is_valid_length", False)
            d_badge = "badge-success" if d_valid else "badge-warning"
            cta_text = desc_obj.get("explicit_cta", "Included")
            st.markdown(
                f"""
                <div class="dark-card">
                    <div class="card-title">📝 Meta Description Specification</div>
                    <div style="margin-bottom:0.75rem;">
                        <span class="badge {d_badge}">{'✅ STRICT 150-170 CHARS' if d_valid else '⚠️ LENGTH OUTSIDE 150-170'} ({desc_len} chars)</span>
                        <span class="badge badge-success">✅ Active Voice</span>
                        <span class="badge badge-info">CTA: {cta_text}</span>
                    </div>
                    <div style="background:#0b1120; border:1px solid #1e293b; border-radius:8px; padding:0.85rem 1rem; color:#cbd5e1; font-size:0.92rem; line-height:1.5;">
                        {desc_text}
                    </div>
                    <div style="margin-top:0.6rem; font-size:0.82rem; color:#94a3b8;">
                        Target range: 150 to 170 characters. Includes persuasive action hook and unambiguous Call To Action.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # =======================================================================
    # TAB 3: On-Page H1-H6 Structure
    # =======================================================================
    with tab3:
        headings = res["heading_tag_outline"]
        h1_text = headings.get("h1", "")
        h2_list = headings.get("h2_sections", [])

        st.markdown(
            """
            <div class="dark-card">
                <div class="card-title">📑 On-Page Heading Hierarchy (H1-H6 Blueprint)</div>
                <div style="margin-bottom:0.85rem;">
                    <span class="badge badge-success">✅ EXACTLY ONE H1 TAG</span>
                    <span class="badge badge-success">✅ PRIMARY KEYWORD INCLUDED</span>
                    <span class="badge badge-info">STRUCTURED H2 & H3 SECTIONS</span>
                </div>
            """,
            unsafe_allow_html=True
        )

        # Single H1 Display
        st.markdown(f'<div class="heading-h1"><span style="color:#818cf8; font-weight:800;">H1 :</span> {h1_text}</div>', unsafe_allow_html=True)

        # H2 & H3 Hierarchy
        for h2_item in h2_list:
            lsi_tags = "".join([f'<span class="badge badge-muted" style="font-size:0.75rem;">🔑 {lsi}</span>' for lsi in h2_item.get("lsi_keywords_used", [])])
            st.markdown(
                f'<div class="heading-h2"><span style="color:#06b6d4; font-weight:700;">H2 :</span> {h2_item.get("h2", "")} &nbsp; {lsi_tags}</div>',
                unsafe_allow_html=True
            )
            for h3_str in h2_item.get("h3_subsections", []):
                st.markdown(f'<div class="heading-h3"><span style="color:#64748b;">↳ H3 :</span> {h3_str}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Checklist for On-Page Headers
        st.markdown(
            """
            <div class="dark-card">
                <div class="card-title">✅ On-Page Header Integrity Checklist</div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.5rem; font-size:0.9rem; color:#cbd5e1;">
                    <div>✔️ <strong>Single H1 per page:</strong> Enforced without duplication.</div>
                    <div>✔️ <strong>Heading Order:</strong> H1 ➔ H2 ➔ H3 hierarchy maintained with 0 level skips.</div>
                    <div>✔️ <strong>LSI Keyword Mapping:</strong> Semantic variants distributed across subheaders.</div>
                    <div>✔️ <strong>Featured Snippet Readiness:</strong> Question-based H2/H3 headers optimized for searchers.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =======================================================================
    # TAB 4: LSI Keywords & Density Analysis
    # =======================================================================
    with tab4:
        st.markdown(
            """
            <div class="dark-card">
                <div class="card-title">📊 Semantic LSI Keywords & Content Density Analysis</div>
                <p style="color:#94a3b8; font-size:0.9rem; margin-bottom:0.75rem;">
                    Target range is strictly <strong>1.0% to 5.0%</strong>. Any term exceeding 5.0% is flagged for <strong>Keyword Stuffing</strong>.
                </p>
            """,
            unsafe_allow_html=True
        )

        # LSI Chips
        lsi_chips_html = "".join([f'<span class="badge badge-info" style="font-size:0.82rem; margin-bottom:0.4rem;">🔑 {kw}</span>' for kw in res.get("lsi_keywords", [])])
        st.markdown(f"**Identified Semantic LSI Variants:**<br>{lsi_chips_html}", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Interactive Content Editor
        st.markdown("#### ✍️ Live Content Draft Editor")
        st.caption("Edit or paste your copy below to re-calculate keyword density dynamically:")
        draft_text = st.text_area(
            "Draft Content",
            value=res.get("sample_content", ""),
            height=160,
            label_visibility="collapsed"
        )

        # Live calculation
        all_eval_kws = [res["seed_keyword"]] + res.get("lsi_keywords", [])
        live_eval = calculate_keyword_density(draft_text, all_eval_kws)

        # Overall Status Alert
        if live_eval["overall_status"] == "FLAGGED_STUFFING":
            st.error("🚨 **KEYWORD STUFFING FLAGGED!** One or more keywords exceed the 5.0% density ceiling. Reduce repetitive mentions to avoid algorithmic search penalties.")
        elif live_eval["overall_status"] == "OPTIMAL":
            st.success("✅ **OPTIMAL DENSITY!** All target and LSI keywords are balanced within the safe 1.0% – 5.0% range.")
        else:
            st.info("ℹ️ **NEEDS EXPANSION:** Some secondary LSI keywords have density < 1.0%. Consider incorporating them naturally in related sections.")

        # Density Dataframe Table
        table_records = []
        for kw, dt in live_eval["keywords"].items():
            is_pk = (kw.lower() == res["seed_keyword"].lower())
            table_records.append({
                "Keyword Role": "⭐ Primary Seed" if is_pk else "🔑 Semantic LSI",
                "Term": kw,
                "Count": dt["occurrences"],
                "Density": f"{dt['density_percent']}%",
                "Target Range": "1.0% – 5.0%",
                "Status": "🚨 STUFFING (>5%)" if dt["is_stuffing"] else ("✅ Optimal (1-5%)" if dt["in_target_range"] else "🟡 Low (<1%)"),
                "Recommendation": dt["message"]
            })

        df_density = pd.DataFrame(table_records)
        st.dataframe(df_density, use_container_width=True, hide_index=True)

else:
    # Landing State when no search has been run yet
    st.markdown(
        """
        <div class="dark-card" style="text-align:center; padding:3rem 1.5rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">⚡</div>
            <h3 style="margin-bottom:0.5rem; color:#f8fafc;">Enter a Seed Keyword to Generate an SEO Intelligence Brief</h3>
            <p style="color:#94a3b8; max-width:600px; margin:0 auto 1.5rem auto; line-height:1.6;">
                Leverage <strong>BM25 exact keyword matching</strong> and <strong>ChromaDB vector embeddings</strong> 
                merged with <strong>Reciprocal Rank Fusion</strong> to retrieve grounded SEO best practices, 
                then synthesize complete briefs with intent, meta tags, and density checks.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
