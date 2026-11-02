"""
Local Knowledge Base of SEO Best Practices.
Each document has an id, title, category, and content body used for retrieval.
"""

SEO_KNOWLEDGE_BASE = [
    {
        "id": "seo-001",
        "title": "Title Tag Optimization",
        "category": "On-Page SEO",
        "content": (
            "Title tags are one of the most important on-page SEO elements. "
            "Keep titles under 60 characters to avoid truncation in SERPs. "
            "Place the primary keyword near the beginning of the title. "
            "Each page must have a unique title tag that accurately describes its content. "
            "Include your brand name at the end separated by a pipe or dash. "
            "Use power words like 'Ultimate', 'Guide', 'Best' to improve CTR."
        ),
    },
    {
        "id": "seo-002",
        "title": "Meta Description Best Practices",
        "category": "On-Page SEO",
        "content": (
            "Meta descriptions should be between 150-160 characters to display fully in search results. "
            "Include the target keyword naturally within the description. "
            "Write compelling, action-oriented copy that encourages clicks. "
            "Each page needs a unique meta description. "
            "Use a clear call-to-action such as 'Learn more', 'Discover', or 'Get started'. "
            "While meta descriptions are not a direct ranking factor, they significantly impact CTR."
        ),
    },
    {
        "id": "seo-003",
        "title": "Header Tag Hierarchy (H1-H6)",
        "category": "On-Page SEO",
        "content": (
            "Use a single H1 tag per page containing the primary keyword. "
            "Structure content with H2 and H3 subheadings for readability and crawlability. "
            "Header tags help search engines understand content hierarchy and topic structure. "
            "Include secondary and LSI keywords in H2/H3 tags naturally. "
            "Avoid skipping heading levels (e.g., jumping from H2 to H4). "
            "Well-structured headers improve both user experience and featured snippet eligibility."
        ),
    },
    {
        "id": "seo-004",
        "title": "Keyword Research Fundamentals",
        "category": "Keyword Strategy",
        "content": (
            "Keyword research is the foundation of any SEO strategy. "
            "Focus on search intent: informational, navigational, transactional, or commercial investigation. "
            "Analyze keyword difficulty (KD), search volume, and CPC to prioritize targets. "
            "Use long-tail keywords (3-5 words) for lower competition and higher conversion rates. "
            "Study competitor keywords using tools like Ahrefs, SEMrush, or Google Keyword Planner. "
            "Group semantically related keywords into topic clusters for comprehensive content coverage."
        ),
    },
    {
        "id": "seo-005",
        "title": "Search Intent Optimization",
        "category": "Keyword Strategy",
        "content": (
            "Search intent is the primary goal a user has when typing a query into a search engine. "
            "There are four main types: informational (how-to, what-is), navigational (brand queries), "
            "transactional (buy, purchase), and commercial investigation (best, review, comparison). "
            "Align your content format with the dominant intent in the SERP. "
            "Informational intent favors blog posts and guides; transactional intent favors product pages. "
            "Mismatched intent is one of the top reasons pages fail to rank despite good on-page SEO."
        ),
    },
    {
        "id": "seo-006",
        "title": "Internal Linking Strategy",
        "category": "On-Page SEO",
        "content": (
            "Internal links distribute page authority and help search engines discover content. "
            "Use descriptive, keyword-rich anchor text for internal links instead of 'click here'. "
            "Link from high-authority pages to important pages that need a ranking boost. "
            "Create a hub-and-spoke model: pillar pages link to cluster content and vice versa. "
            "Aim for at least 3-5 internal links per page to related content. "
            "Regularly audit internal links to fix broken links and optimize anchor text distribution."
        ),
    },
    {
        "id": "seo-007",
        "title": "Backlink Building Strategies",
        "category": "Off-Page SEO",
        "content": (
            "Backlinks from authoritative, relevant websites remain a top-3 Google ranking factor. "
            "Focus on earning high-quality links through content marketing, guest blogging, and digital PR. "
            "The most effective link-building content types are original research, infographics, and tools. "
            "Avoid spammy link schemes, PBNs, and paid links that violate Google's guidelines. "
            "Monitor your backlink profile with Ahrefs or Moz to disavow toxic links. "
            "Domain authority (DA) and domain rating (DR) of linking sites matter more than link quantity."
        ),
    },
    {
        "id": "seo-008",
        "title": "Technical SEO: Site Speed Optimization",
        "category": "Technical SEO",
        "content": (
            "Page speed is a confirmed Google ranking factor, especially for mobile searches. "
            "Core Web Vitals (LCP, FID/INP, CLS) directly impact search rankings since 2021. "
            "Optimize images using WebP format and lazy loading to reduce initial page load time. "
            "Minify CSS, JavaScript, and HTML; use browser caching and CDN for static assets. "
            "Target an LCP under 2.5 seconds, FID/INP under 200ms, and CLS under 0.1 for good scores. "
            "Use Google PageSpeed Insights and Lighthouse to diagnose and fix performance issues."
        ),
    },
    {
        "id": "seo-009",
        "title": "Mobile-First Indexing",
        "category": "Technical SEO",
        "content": (
            "Google predominantly uses the mobile version of content for indexing and ranking. "
            "Ensure your website uses responsive design that adapts to all screen sizes. "
            "Mobile pages must have the same content, structured data, and meta tags as desktop. "
            "Test mobile usability with Google's Mobile-Friendly Test and Search Console reports. "
            "Avoid intrusive interstitials and pop-ups that degrade mobile user experience. "
            "Mobile page speed is critical: compress resources and minimize render-blocking scripts."
        ),
    },
    {
        "id": "seo-010",
        "title": "Schema Markup and Structured Data",
        "category": "Technical SEO",
        "content": (
            "Schema markup helps search engines understand your content and can generate rich snippets. "
            "Common schema types include Article, Product, FAQ, HowTo, LocalBusiness, and Review. "
            "Use JSON-LD format (recommended by Google) to implement structured data. "
            "Rich results like star ratings, FAQs, and product info significantly boost CTR. "
            "Validate your markup with Google's Rich Results Test and Schema.org validator. "
            "Implement breadcrumb schema, sitelinks searchbox, and organization schema for brand authority."
        ),
    },
    {
        "id": "seo-011",
        "title": "Content Quality and E-E-A-T",
        "category": "Content Strategy",
        "content": (
            "E-E-A-T stands for Experience, Expertise, Authoritativeness, and Trustworthiness. "
            "Google's Search Quality Rater Guidelines emphasize E-E-A-T for ranking content. "
            "Demonstrate first-hand experience on topics, especially for YMYL (Your Money Your Life) pages. "
            "Include author bios with credentials, link to authoritative sources, and cite data. "
            "Comprehensive, well-researched content that satisfies user intent outranks thin content. "
            "Regularly update existing content to keep it accurate, fresh, and competitive."
        ),
    },
    {
        "id": "seo-012",
        "title": "Content-Length and Depth Guidelines",
        "category": "Content Strategy",
        "content": (
            "Long-form content (1500-2500+ words) tends to rank higher for competitive keywords. "
            "Focus on content depth and comprehensiveness rather than arbitrary word counts. "
            "Cover related subtopics thoroughly to satisfy the full spectrum of search intent. "
            "Use the skyscraper technique: find top-ranking content and create something significantly better. "
            "Break long content into scannable sections with headers, bullets, tables, and visuals. "
            "Include a table of contents for posts over 1500 words to improve UX and jump-link potential."
        ),
    },
    {
        "id": "seo-013",
        "title": "Image SEO Optimization",
        "category": "On-Page SEO",
        "content": (
            "Optimize image file names with descriptive, keyword-rich names before uploading. "
            "Write meaningful alt text that describes the image and includes target keywords naturally. "
            "Compress images to reduce file size without losing visual quality using tools like TinyPNG. "
            "Use modern formats like WebP or AVIF for better compression and faster load times. "
            "Implement responsive images with srcset to serve appropriate sizes for different devices. "
            "Add images to your XML sitemap or use an image sitemap for better indexation."
        ),
    },
    {
        "id": "seo-014",
        "title": "URL Structure Best Practices",
        "category": "Technical SEO",
        "content": (
            "Keep URLs short, descriptive, and include the target keyword. "
            "Use hyphens to separate words in URLs; avoid underscores, spaces, or special characters. "
            "Implement a logical URL hierarchy that reflects site structure (e.g., /category/subcategory/page). "
            "Avoid dynamic parameters and session IDs in URLs when possible. "
            "Use canonical tags to prevent duplicate content issues from URL variations. "
            "Set up proper 301 redirects when changing URLs to preserve link equity and avoid 404 errors."
        ),
    },
    {
        "id": "seo-015",
        "title": "Local SEO Optimization",
        "category": "Local SEO",
        "content": (
            "Claim and optimize your Google Business Profile with accurate NAP (Name, Address, Phone). "
            "Encourage and respond to customer reviews; review signals influence local pack rankings. "
            "Build local citations on directories like Yelp, Yellow Pages, and industry-specific platforms. "
            "Use location-specific keywords in title tags, meta descriptions, headers, and content. "
            "Create dedicated landing pages for each location or service area your business covers. "
            "Implement LocalBusiness schema markup with geo-coordinates and business hours."
        ),
    },
    {
        "id": "seo-016",
        "title": "XML Sitemap and Robots.txt",
        "category": "Technical SEO",
        "content": (
            "XML sitemaps help search engines discover and crawl all important pages on your site. "
            "Include only canonical, indexable pages in your sitemap; exclude noindex or redirected URLs. "
            "Submit your sitemap to Google Search Console and Bing Webmaster Tools. "
            "Keep sitemaps under 50,000 URLs and 50MB; use sitemap index files for larger sites. "
            "Robots.txt controls crawler access; use it to block crawling of admin, duplicate, or low-value pages. "
            "Never block CSS or JS files in robots.txt as Google needs them to render pages properly."
        ),
    },
    {
        "id": "seo-017",
        "title": "Core Web Vitals Deep Dive",
        "category": "Technical SEO",
        "content": (
            "Largest Contentful Paint (LCP) measures loading performance of the largest visible element. "
            "Interaction to Next Paint (INP) replaced FID in 2024 to measure overall page responsiveness. "
            "Cumulative Layout Shift (CLS) measures visual stability; avoid elements that shift during loading. "
            "Optimize LCP by preloading hero images, using CDN, and reducing server response time (TTFB). "
            "Improve INP by breaking long JavaScript tasks, using web workers, and optimizing event handlers. "
            "Fix CLS by setting explicit dimensions on images/ads and avoiding dynamic content injection above the fold."
        ),
    },
    {
        "id": "seo-018",
        "title": "Content Freshness and Updates",
        "category": "Content Strategy",
        "content": (
            "Google's freshness algorithm favors recently updated content for time-sensitive queries. "
            "Regularly audit and update existing content with new data, statistics, and examples. "
            "Add a 'Last Updated' date to show users and search engines that content is current. "
            "Republishing updated content can recover lost rankings and drive renewed traffic. "
            "Create an evergreen content strategy that combines timeless topics with regular updates. "
            "Monitor content decay using analytics to identify pages losing traffic that need refreshing."
        ),
    },
    {
        "id": "seo-019",
        "title": "Featured Snippets Optimization",
        "category": "Content Strategy",
        "content": (
            "Featured snippets appear above organic results (position zero) and capture significant traffic. "
            "Target snippet opportunities by answering questions directly in 40-60 words for paragraph snippets. "
            "Use ordered/unordered lists and tables formatted in HTML for list and table snippet types. "
            "Structure content with question-based H2/H3 headers matching common search queries. "
            "Pages ranking in positions 1-5 are most likely to win featured snippets. "
            "Analyze existing snippets for your target keywords to understand the format Google prefers."
        ),
    },
    {
        "id": "seo-020",
        "title": "Topical Authority and Content Clusters",
        "category": "Content Strategy",
        "content": (
            "Topical authority is built by creating comprehensive content clusters around core subjects. "
            "A pillar page covers a broad topic, while cluster pages dive deep into subtopics. "
            "Interlink all cluster content to the pillar page and to each other to signal topical depth. "
            "Sites with strong topical authority rank faster for new content within their niche. "
            "Conduct a content gap analysis to identify missing subtopics in your clusters. "
            "Use tools like MarketMuse or Clearscope to evaluate topical completeness and content scores."
        ),
    },
    {
        "id": "seo-021",
        "title": "Link Anchor Text Optimization",
        "category": "Off-Page SEO",
        "content": (
            "Anchor text diversity is crucial; avoid over-optimization with exact-match anchors. "
            "A natural anchor text profile includes branded, generic, partial-match, and naked URL anchors. "
            "Google's Penguin algorithm penalizes sites with unnatural anchor text patterns. "
            "Use descriptive anchors that give users and crawlers context about the linked page's content. "
            "Monitor anchor text distribution across your backlink profile monthly. "
            "For internal links, use keyword-rich anchors more freely than for external backlinks."
        ),
    },
    {
        "id": "seo-022",
        "title": "Crawl Budget Optimization",
        "category": "Technical SEO",
        "content": (
            "Crawl budget is the number of pages a search engine bot will crawl on your site in a given time. "
            "Large sites (100k+ pages) must optimize crawl budget to ensure important pages are indexed. "
            "Block low-value pages (filters, sorts, internal search results) via robots.txt or noindex. "
            "Fix crawl errors, redirect chains, and soft 404s that waste crawl budget. "
            "Improve site speed and server response time to allow Googlebot to crawl more pages per visit. "
            "Use Google Search Console's Crawl Stats report to monitor crawl rate and identify issues."
        ),
    },
    {
        "id": "seo-023",
        "title": "Voice Search Optimization",
        "category": "Keyword Strategy",
        "content": (
            "Voice search queries are typically longer and more conversational than typed searches. "
            "Optimize for question-based keywords: who, what, where, when, why, and how queries. "
            "Featured snippets are the primary source for voice search answers on smart speakers. "
            "Target natural language phrases and long-tail conversational keywords. "
            "Ensure your site loads fast and is mobile-friendly, as voice searches are predominantly mobile. "
            "Local businesses should optimize for 'near me' queries which are common in voice search."
        ),
    },
    {
        "id": "seo-024",
        "title": "International SEO (hreflang)",
        "category": "Technical SEO",
        "content": (
            "Use hreflang tags to tell Google which language and regional version of a page to show users. "
            "Implement hreflang in the HTML head, HTTP headers, or XML sitemap for multilingual sites. "
            "Each hreflang annotation must have a reciprocal tag on the referenced page. "
            "Use x-default hreflang for the fallback page when no language/region match exists. "
            "Choose between ccTLD (.de, .fr), subdirectory (/de/, /fr/), or subdomain (de.example.com) strategies. "
            "Avoid auto-redirecting users based on IP; let Google index each language version independently."
        ),
    },
    {
        "id": "seo-025",
        "title": "SEO Analytics and KPI Tracking",
        "category": "SEO Analytics",
        "content": (
            "Track organic traffic, keyword rankings, CTR, bounce rate, and conversions as core SEO KPIs. "
            "Use Google Search Console for impressions, clicks, average position, and indexing status. "
            "Set up Google Analytics 4 (GA4) goals and events to measure SEO-driven conversions. "
            "Monitor keyword ranking movements weekly; sudden drops may indicate algorithm updates or penalties. "
            "Track page-level metrics to identify top performers and underperforming content for optimization. "
            "Create monthly SEO reports with trend analysis, action items, and ROI calculations."
        ),
    },
]

