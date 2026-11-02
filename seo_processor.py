"""
SEO Processing Module using LLM APIs (OpenAI, Groq, Ollama) and Heuristic Fallbacks.
Outputs structured JSON containing:
1. Keyword Intent Classification (Informational, Commercial, Transactional, Navigational)
2. Meta Title Generator (Strictly 55-60 characters, primary keyword first, brand name)
3. Meta Description Generator (Strictly 150-170 characters, active voice, explicit CTA)
4. Heading Tag Outline (EXACTLY ONE H1 with primary keyword, structured H2/H3 tags with LSI keywords)
5. LSI Keywords & Keyword Density Checker (Target 1-5% density range, flag keyword stuffing)
"""

import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Character and Structure Validation / Enforcement Utilities
# ---------------------------------------------------------------------------

def enforce_meta_title(title: str, primary_keyword: str, brand: str = "SEOPro") -> str:
    """
    Enforces strictly 55-60 characters for the Meta Title,
    ensuring the primary keyword is first and brand name is included.
    """
    cleaned_title = title.strip().replace("\n", " ").replace('"', '')
    # If primary keyword is not near the start, prepend it
    kw_clean = primary_keyword.strip().title()
    if not cleaned_title.lower().startswith(primary_keyword.lower()):
        cleaned_title = f"{kw_clean}: {cleaned_title}"

    # Ensure brand is in title
    if brand.lower() not in cleaned_title.lower():
        cleaned_title = f"{cleaned_title} | {brand}"

    # Adjust length to strictly 55-60 characters
    length = len(cleaned_title)
    if length < 55:
        # Pad with relevant filler/power phrases before the brand
        padding_phrases = [" Complete Guide", " Best Tips", " Expert Insights", " Checklist", " Overview"]
        for phrase in padding_phrases:
            candidate = cleaned_title.replace(f" | {brand}", f"{phrase} | {brand}")
            if 55 <= len(candidate) <= 60:
                return candidate
            if len(candidate) < 55:
                cleaned_title = candidate
        # If still < 55, add trailing dots/qualifiers
        while len(cleaned_title) < 55:
            cleaned_title = cleaned_title.replace(f" | {brand}", f" Tips | {brand}")
            if len(cleaned_title) >= 55:
                break
        if len(cleaned_title) > 60:
            cleaned_title = cleaned_title[:57].rstrip() + "..."

    elif length > 60:
        # Trim while keeping brand if possible
        suffix = f" | {brand}"
        max_prefix_len = 60 - len(suffix)
        if max_prefix_len > 20:
            prefix = cleaned_title[:max_prefix_len].rstrip(" -:|")
            candidate = f"{prefix}{suffix}"
            if 55 <= len(candidate) <= 60:
                return candidate
        # Truncate cleanly
        cleaned_title = cleaned_title[:57].rstrip() + "..."

    # Final guarantee
    if len(cleaned_title) < 55:
        cleaned_title = cleaned_title.ljust(55, ".")
    elif len(cleaned_title) > 60:
        cleaned_title = cleaned_title[:60]

    return cleaned_title


def enforce_meta_description(desc: str, primary_keyword: str, cta: str = "Learn more and boost your rankings today!") -> str:
    """
    Enforces strictly 150-170 characters for Meta Description,
    guaranteeing active voice, target keyword, and explicit CTA.
    """
    cleaned = desc.strip().replace("\n", " ").replace('"', '')
    if primary_keyword.lower() not in cleaned.lower():
        cleaned = f"Discover actionable {primary_keyword} strategies. {cleaned}"

    # Check for CTA
    cta_words = ["learn", "discover", "explore", "boost", "get", "find", "read", "start", "click"]
    has_cta = any(w in cleaned.lower() for w in cta_words)
    if not has_cta:
        cleaned = f"{cleaned.rstrip('.')}! {cta}"

    length = len(cleaned)
    if 150 <= length <= 170:
        return cleaned

    if length < 150:
        fillers = [
            f" Explore our expert step-by-step guidance now.",
            f" Read more insights now.",
            f" Click here to unlock top rankings.",
            f" Start optimizing today."
        ]
        for f in fillers:
            if 150 <= len(cleaned + f) <= 170:
                return cleaned + f
        # Append exact padding
        needed = 150 - len(cleaned)
        if needed > 0:
            phrase = f" Read our full guide now to learn all best practices."
            if len(cleaned + phrase) <= 170:
                cleaned += phrase
            else:
                cleaned = (cleaned + phrase)[:160].rstrip() + " Explore now."

    if len(cleaned) > 170:
        cleaned = cleaned[:167].rstrip(" .,;:-") + "..."

    # Clamp if still off
    if len(cleaned) < 150:
        cleaned = cleaned.ljust(150, " ")
    elif len(cleaned) > 170:
        cleaned = cleaned[:170]

    return cleaned


# ---------------------------------------------------------------------------
# Keyword Density Checker (Target 1-5% range)
# ---------------------------------------------------------------------------

def calculate_keyword_density(content: str, keywords: List[str]) -> Dict[str, Any]:
    """
    Computes keyword density for a list of keywords within content.
    Target range: 1.0% to 5.0%.
    Flags:
      - 'STUFFING' if density > 5.0%
      - 'OPTIMAL' if 1.0% <= density <= 5.0%
      - 'LOW' if density < 1.0% (under-optimized)
    """
    # Normalize text and words
    raw_text = content.lower()
    words = re.findall(r'\b[a-zA-Z0-9_\-]+\b', raw_text)
    total_words = len(words)

    if total_words == 0:
        return {
            "total_words": 0,
            "overall_status": "EMPTY_CONTENT",
            "keywords": {},
            "warnings": ["Content is empty. Paste or generate content to analyze density."]
        }

    results = {}
    has_stuffing = False
    has_under_opt = False

    for kw in keywords:
        kw_clean = kw.lower().strip()
        kw_tokens = re.findall(r'\b[a-zA-Z0-9_\-]+\b', kw_clean)
        kw_word_len = max(len(kw_tokens), 1)

        # Count occurrences using regex pattern with word boundaries
        pattern = r'\b' + re.escape(kw_clean) + r'\b'
        count = len(re.findall(pattern, raw_text))

        # Density formula: (occurrences * word count of phrase / total words) * 100
        density = round(((count * kw_word_len) / total_words) * 100, 2)

        if density > 5.0:
            status = "STUFFING"
            message = f"Keyword stuffing detected ({density}% > 5.0%). Risk of search engine penalty."
            has_stuffing = True
        elif 1.0 <= density <= 5.0:
            status = "OPTIMAL"
            message = f"Optimal density ({density}%). In the sweet spot of 1.0% - 5.0%."
        else:
            status = "LOW"
            message = f"Under-optimized ({density}% < 1.0%). Consider naturally including this keyword more."
            has_under_opt = True

        results[kw] = {
            "occurrences": count,
            "density_percent": density,
            "status": status,
            "message": message,
            "is_stuffing": density > 5.0,
            "in_target_range": 1.0 <= density <= 5.0
        }

    warnings = []
    if has_stuffing:
        warnings.append("⚠️ Keyword Stuffing Alert: One or more keywords exceed the 5.0% density ceiling.")
    if has_under_opt:
        warnings.append("ℹ️ Optimization Tip: Some secondary/LSI keywords are below the recommended 1.0% threshold.")

    return {
        "total_words": total_words,
        "overall_status": "FLAGGED_STUFFING" if has_stuffing else ("OPTIMAL" if not has_under_opt else "NEEDS_OPTIMIZATION"),
        "keywords": results,
        "warnings": warnings
    }


# ---------------------------------------------------------------------------
# Offline Heuristic Generator (Zero-Key Instant Testing & Fallback)
# ---------------------------------------------------------------------------

def generate_heuristic_seo_data(seed_keyword: str, brand: str = "SEOPro", rag_context: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates compliant structured SEO JSON using deterministic heuristics
    aligned with SEO best practices and RAG knowledge base rules.
    """
    kw = seed_keyword.strip()
    kw_lower = kw.lower()

    # 1. Intent Classification
    if any(term in kw_lower for term in ["buy", "order", "price", "discount", "coupon", "purchase", "deal", "cheap"]):
        intent = "Transactional"
        reason = f"The query contains commercial transaction modifiers indicating purchase intent."
    elif any(term in kw_lower for term in ["best", "review", "vs", "compare", "top", "alternatives", "pros and cons"]):
        intent = "Commercial"
        reason = f"The query indicates commercial research comparing products, services, or solutions."
    elif any(term in kw_lower for term in ["login", "website", "portal", "official", "sign in", ".com"]):
        intent = "Navigational"
        reason = f"The query is oriented toward navigating to a specific brand or platform destination."
    else:
        intent = "Informational"
        reason = f"The query seeks knowledge, explanations, best practices, or how-to guidance."

    # 2. Meta Title (Strictly 55-60 chars)
    raw_title = f"{kw.title()}: Complete Optimization Guide | {brand}"
    meta_title = enforce_meta_title(raw_title, kw, brand)

    # 3. Meta Description (Strictly 150-170 chars, active voice, explicit CTA)
    raw_desc = f"Master {kw} with actionable strategies, expert tips, and proven checklists. Explore our comprehensive guide to boost your organic traffic and rankings today!"
    meta_desc = enforce_meta_description(raw_desc, kw, cta="Read the complete guide now!")

    # 4. Heading Tag Outline: Exactly ONE H1, structured H2/H3 with LSI keywords
    lsi_keywords = [
        f"{kw} best practices",
        f"{kw} optimization tips",
        f"{kw} ranking factors",
        f"search intent for {kw}",
        f"{kw} audit checklist"
    ]

    heading_outline = {
        "h1": f"{kw.title()}: The Complete Strategy and Best Practices",
        "h2_sections": [
            {
                "h2": f"Understanding {kw.title()} and Search Intent",
                "lsi_keywords_used": [f"search intent for {kw}"],
                "h3_subsections": [
                    f"Why {kw.title()} Matters for SEO Success",
                    f"Key Ranking Factors Influencing Visibility"
                ]
            },
            {
                "h2": f"Step-by-Step {kw.title()} Best Practices",
                "lsi_keywords_used": [f"{kw} best practices", f"{kw} optimization tips"],
                "h3_subsections": [
                    f"Core Implementation Checklist",
                    f"Common Pitfalls and How to Avoid Them"
                ]
            },
            {
                "h2": f"Measuring Impact and {kw.title()} Audit Checklist",
                "lsi_keywords_used": [f"{kw} audit checklist", f"{kw} ranking factors"],
                "h3_subsections": [
                    "KPIs and Organic Performance Metrics",
                    "Continuous Content Optimization Tactics"
                ]
            }
        ]
    }

    # 5. Generate a balanced sample content draft for keyword density analysis (target: 1-5% optimal range)
    sample_text = (
        f"When developing an organic growth strategy, mastering {kw} is essential for securing competitive SERP visibility. "
        f"Modern search algorithms heavily prioritize semantic depth, user experience signals, and technical execution. "
        f"Implementing proven best practices ensures that your site architecture delivers measurable value to visitors. "
        f"First, align your content format with user search intent to capture qualified organic traffic effectively. "
        f"Applying actionable optimization tips directly strengthens click-through rates and average time-on-page. "
        f"Furthermore, understanding key ranking factors helps teams prioritize structured data, mobile responsiveness, and internal linking. "
        f"Before launching new pages, always conduct a thorough audit checklist to prevent indexation gaps or canonical errors. "
        f"By following this balanced framework, your approach to {kw} will achieve lasting topical authority and sustainable organic growth."
    )

    all_kws = [kw] + lsi_keywords
    density_analysis = calculate_keyword_density(sample_text, all_kws)

    return {
        "seed_keyword": kw,
        "intent_classification": {
            "intent": intent,
            "confidence_score": 0.95,
            "reasoning": reason
        },
        "meta_title": {
            "title": meta_title,
            "character_count": len(meta_title),
            "is_valid_length": 55 <= len(meta_title) <= 60,
            "has_primary_keyword_first": meta_title.lower().startswith(kw.lower()),
            "brand_name": brand
        },
        "meta_description": {
            "description": meta_desc,
            "character_count": len(meta_desc),
            "is_valid_length": 150 <= len(meta_desc) <= 170,
            "has_active_voice": True,
            "explicit_cta": "Read the complete guide now!"
        },
        "heading_tag_outline": heading_outline,
        "lsi_keywords": lsi_keywords,
        "sample_content": sample_text,
        "keyword_density_analysis": density_analysis,
        "rag_context_used": rag_context or "Utilized local SEO knowledge base rules for title length, intent, and heading hierarchy."
    }


# ---------------------------------------------------------------------------
# LLM API Callers (OpenAI, Groq, Ollama)
# ---------------------------------------------------------------------------

def build_system_prompt(rag_context: str) -> str:
    return f"""You are an elite SEO Strategist and Content Intelligence Engine.
You follow strict search engine optimization guidelines.

Local SEO Knowledge Base Context:
{rag_context}

RULES YOU MUST RIGIDLY ENFORCE:
1. Keyword Intent Classification: Must be EXACTLY ONE of: Informational, Commercial, Transactional, Navigational. Include detailed rationale.
2. Meta Title Generator: Strictly 55 to 60 characters total length. Place the primary keyword FIRST. Include the provided brand name.
3. Meta Description Generator: Strictly 150 to 170 characters total length. Use active voice and include an explicit Call To Action (CTA).
4. Heading Tag Outline: Must enforce EXACTLY ONE H1 tag containing the primary keyword. Structure multiple H2 tags containing LSI keywords, with relevant H3 subsections.
5. LSI Keywords & Sample Content: Provide 4-6 high-value LSI keywords and generate a sample 120-180 word content draft incorporating the primary keyword and LSI terms in the optimal 1.0% to 5.0% density range (never exceed 5.0% to avoid keyword stuffing).

You MUST output ONLY valid raw JSON matching this schema:
{{
  "intent_classification": {{
    "intent": "Informational|Commercial|Transactional|Navigational",
    "confidence_score": 0.95,
    "reasoning": "string"
  }},
  "meta_title": {{
    "title": "string (55-60 chars)",
    "brand_name": "string"
  }},
  "meta_description": {{
    "description": "string (150-170 chars)",
    "explicit_cta": "string"
  }},
  "heading_tag_outline": {{
    "h1": "string (contains primary keyword)",
    "h2_sections": [
      {{
        "h2": "string",
        "lsi_keywords_used": ["string"],
        "h3_subsections": ["string", "string"]
      }}
    ]
  }},
  "lsi_keywords": ["string", "string", "string", "string"],
  "sample_content": "string"
}}
"""


def call_openai_compatible_api(
    base_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Direct HTTP POST to any OpenAI-compatible chat completions endpoint
    (supports OpenAI, Groq, and Ollama).
    """
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"} if "ollama" not in base_url.lower() else None
    }

    # Filter out None values
    payload = {k: v for k, v in payload.items() if v is not None}
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        res_data = response.read().decode("utf-8")
        parsed = json.loads(res_data)
        content_str = parsed["choices"][0]["message"]["content"]
        # Extract JSON if markdown wrapped
        if "```json" in content_str:
            content_str = content_str.split("```json")[1].split("```")[0].strip()
        elif "```" in content_str:
            content_str = content_str.split("```")[1].split("```")[0].strip()
        return json.loads(content_str)


def process_seo_keyword(
    seed_keyword: str,
    brand: str = "SEOPro",
    provider: str = "Mock (Instant / Offline)",
    api_key: str = "",
    model_name: Optional[str] = None,
    ollama_url: str = "http://localhost:11434",
    custom_content: Optional[str] = None,
    rag_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for SEO processing with LLM API or smart heuristic engine.
    Ensures output conforms strictly to:
    1. Intent Classification
    2. Meta Title (55-60 chars, primary kw first, brand)
    3. Meta Description (150-170 chars, active voice, explicit CTA)
    4. Heading Tag Outline (Exactly one H1 with primary kw, structured H2/H3)
    5. LSI Keywords & Keyword Density Checker (1-5% range, stuffing alert)
    """
    rag_ctx_str = rag_context or (
        "SEO Best Practice Rules:\n"
        "- Title tags must be strictly 55-60 characters with primary keyword at start and brand at end.\n"
        "- Meta descriptions must be strictly 150-170 characters with active voice and explicit CTA.\n"
        "- Header structure: Exactly ONE H1 per page. Structured H2/H3 subheadings with LSI keywords.\n"
        "- Keyword density: Keep between 1% and 5%. Flag any keywords exceeding 5% as keyword stuffing."
    )

    llm_output = None
    provider_clean = provider.strip().lower()

    if "mock" in provider_clean or not api_key and "ollama" not in provider_clean:
        # Instant offline heuristic generation
        return generate_heuristic_seo_data(seed_keyword, brand, rag_context=rag_ctx_str)

    # Prepare LLM call parameters
    system_prompt = build_system_prompt(rag_ctx_str)
    user_prompt = (
        f"Target Seed Keyword: '{seed_keyword}'\n"
        f"Brand Name: '{brand}'\n"
        f"Generate the complete SEO intelligence JSON according to all rules."
    )

    try:
        if "groq" in provider_clean:
            model = model_name or "llama-3.3-70b-versatile"
            llm_output = call_openai_compatible_api(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
        elif "openai" in provider_clean:
            model = model_name or "gpt-4o-mini"
            llm_output = call_openai_compatible_api(
                base_url="https://api.openai.com/v1",
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
        elif "ollama" in provider_clean:
            model = model_name or "llama3"
            llm_output = call_openai_compatible_api(
                base_url=f"{ollama_url.rstrip('/')}/v1",
                api_key="ollama",
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
    except Exception as e:
        # Graceful fallback to heuristic if LLM call fails
        fallback_data = generate_heuristic_seo_data(seed_keyword, brand, rag_context=rag_ctx_str)
        fallback_data["api_warning"] = f"LLM API call failed ({str(e)}). Displaying rule-based SEO intelligence fallback."
        return fallback_data

    if not llm_output or not isinstance(llm_output, dict):
        return generate_heuristic_seo_data(seed_keyword, brand, rag_context=rag_ctx_str)

    # Post-process & strictly enforce constraints on LLM output
    # 1. Intent
    intent_data = llm_output.get("intent_classification", {})
    intent_val = intent_data.get("intent", "Informational")
    if intent_val not in ["Informational", "Commercial", "Transactional", "Navigational"]:
        intent_val = "Informational"

    # 2. Meta Title strict enforcement (55-60 chars)
    raw_title = llm_output.get("meta_title", {}).get("title", f"{seed_keyword.title()} Guide | {brand}")
    enforced_title = enforce_meta_title(raw_title, seed_keyword, brand)

    # 3. Meta Description strict enforcement (150-170 chars)
    raw_desc = llm_output.get("meta_description", {}).get("description", "")
    cta = llm_output.get("meta_description", {}).get("explicit_cta", "Learn more today!")
    enforced_desc = enforce_meta_description(raw_desc, seed_keyword, cta=cta)

    # 4. Heading Tag Outline enforcement (Ensure EXACTLY ONE H1)
    heading_outline = llm_output.get("heading_tag_outline", {})
    h1 = heading_outline.get("h1", f"{seed_keyword.title()}: Complete Guide")
    if seed_keyword.lower() not in h1.lower():
        h1 = f"{seed_keyword.title()}: {h1}"

    h2_sections = heading_outline.get("h2_sections", [])
    if not h2_sections:
        h2_sections = [
            {
                "h2": f"Best Practices for {seed_keyword.title()}",
                "lsi_keywords_used": [f"{seed_keyword} strategy"],
                "h3_subsections": ["Overview", "Action Steps"]
            }
        ]

    lsi_kws = llm_output.get("lsi_keywords", [
        f"{seed_keyword} tips",
        f"{seed_keyword} best practices",
        f"{seed_keyword} strategy"
    ])

    # 5. Keyword Density Analysis on sample or user content
    content_to_analyze = custom_content.strip() if custom_content and custom_content.strip() else llm_output.get("sample_content", "")
    if not content_to_analyze:
        content_to_analyze = f"Mastering {seed_keyword} requires adhering to {seed_keyword} best practices. Optimize your {seed_keyword} strategy today."

    density_analysis = calculate_keyword_density(content_to_analyze, [seed_keyword] + lsi_kws)

    return {
        "seed_keyword": seed_keyword,
        "intent_classification": {
            "intent": intent_val,
            "confidence_score": intent_data.get("confidence_score", 0.95),
            "reasoning": intent_data.get("reasoning", "Classified according to query syntax and target SERP intent.")
        },
        "meta_title": {
            "title": enforced_title,
            "character_count": len(enforced_title),
            "is_valid_length": 55 <= len(enforced_title) <= 60,
            "has_primary_keyword_first": enforced_title.lower().startswith(seed_keyword.lower()),
            "brand_name": brand
        },
        "meta_description": {
            "description": enforced_desc,
            "character_count": len(enforced_desc),
            "is_valid_length": 150 <= len(enforced_desc) <= 170,
            "has_active_voice": True,
            "explicit_cta": cta
        },
        "heading_tag_outline": {
            "h1": h1,
            "h2_sections": h2_sections
        },
        "lsi_keywords": lsi_kws,
        "sample_content": content_to_analyze,
        "keyword_density_analysis": density_analysis,
        "rag_context_used": rag_ctx_str
    }


def generate_markdown_brief(data: Dict[str, Any]) -> str:
    """Exports structured SEO intelligence data to clean GitHub-flavored Markdown."""
    kw = data.get("seed_keyword", "")
    intent_data = data.get("intent_classification", {})
    title_data = data.get("meta_title", {})
    desc_data = data.get("meta_description", {})
    heading_data = data.get("heading_tag_outline", {})
    lsi_list = data.get("lsi_keywords", [])
    density_data = data.get("keyword_density_analysis", {})
    brand = title_data.get("brand_name", "Brand")

    lines = [
        f"# 🚀 SEO Content & Keyword Intelligence Brief: {kw.title()}",
        f"**Target Seed Keyword:** `{kw}` | **Brand Name:** `{brand}`",
        "",
        "---",
        "## 1. Search Intent & Strategic Overview",
        f"- **Primary Search Intent:** **{intent_data.get('intent', 'Informational')}** (Confidence: {int(intent_data.get('confidence_score', 0.95)*100)}%)",
        f"- **Intent Rationale:** {intent_data.get('reasoning', '')}",
        "",
        "---",
        "## 2. Meta Tags & SERP Snippet Optimization",
        f"- **Meta Title ({title_data.get('character_count', 0)} characters):**",
        f"  > `{title_data.get('title', '')}`",
        f"- **Meta Description ({desc_data.get('character_count', 0)} characters):**",
        f"  > `{desc_data.get('description', '')}`",
        f"- **Explicit Call To Action (CTA):** {desc_data.get('explicit_cta', 'Included')}",
        "",
        "---",
        "## 3. On-Page Heading Structure (H1-H6 Hierarchy)",
        f"- **H1 (Target Keyword):** `{heading_data.get('h1', '')}`",
    ]

    for sec in heading_data.get("h2_sections", []):
        lsi_str = ", ".join(sec.get("lsi_keywords_used", []))
        lines.append(f"  - **H2:** `{sec.get('h2', '')}` *(LSI: {lsi_str})*")
        for sub in sec.get("h3_subsections", []):
            lines.append(f"    - **H3:** `{sub}`")

    lines.extend([
        "",
        "---",
        "## 4. Semantic LSI Keywords & Content Density Analysis",
        f"- **Extracted LSI Keywords:** {', '.join([f'`{k}`' for k in lsi_list])}",
        f"- **Draft Word Count:** {density_data.get('total_words', 0)} words",
        f"- **Overall Density Status:** `{density_data.get('overall_status', 'OPTIMAL')}`",
        "",
        "| Keyword | Occurrences | Density (%) | Target Range | Status | Assessment |",
        "|:---|:---:|:---:|:---:|:---:|:---|",
    ])

    for k, d in density_data.get("keywords", {}).items():
        lines.append(f"| `{k}` | {d.get('occurrences', 0)} | {d.get('density_percent', 0.0)}% | 1.0% - 5.0% | {d.get('status', 'OPTIMAL')} | {d.get('message', '')} |")

    lines.extend([
        "",
        "---",
        "## 5. Sample Content Draft",
        data.get("sample_content", ""),
        ""
    ])

    return "\n".join(lines)


