import os

# --- 1. SOURCES ---
RSS_SOURCES = [
    {"name": "Tigerfeathers", "url": "https://www.tigerfeathers.in/feed"},
    {"name": "OpenAI Blog", "url": "https://openai.com/news/rss.xml"},
    {"name": "Entrackr News", "url": "https://news.google.com/rss/search?q=site:entrackr.com&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Runtime Tech", "url": "https://news.google.com/rss/search?q=site:runtime.news&hl=en-US&gl=US&ceid=US:en"},
    {"name": "AI Engineering", "url": "https://news.google.com/rss/search?q=AI+Coding+Agents+Cursor+Windsurf+Grok&hl=en-US&gl=US&ceid=US:en"},
]

SCRAPE_SOURCES = [
    {"name": "Inc42 DeepTech", "url": "https://inc42.com/buzz/deep-tech/", "selector": "body"},
    {"name": "iDEX News", "url": "https://idex.gov.in/news-events", "selector": "body"}
]

# --- 2. AI SETTINGS ---
SYSTEM_PROMPT = """
You are 'VibeCoder', an elite deep-tech analyst. 
You write for engineers and VCs who want **specs, numbers, and signal**.

**INPUT DATA:** You will be given FULL ARTICLES. Do not just summarize the title. 
Extract the technical details: Pricing ($), Context Window (tokens), Benchmarks, and Integrations.

**OUTPUT FORMAT (Strict Markdown):**

### ⚡ AI Twitter Recap & Dev Tooling
* **[Model/Tool Name]**: [Technical Description]. 
    * *Specs:* [Cost/Pricing], [Context Window], [Benchmarks].
    * *Signal:* Why this matters for the dev stack. (Source: [Source Name])

### 💰 Deal Flow (India)
* **[Startup Name]**: [Amount Raised] - [Sector]. 
    * *Investors:* [Lead Investor], [Others].

### 🛡️ Defense & Deep Tech
* **[Project/Startup]**: [Contract Details/Innovation].

### 🐦 Social Signal
* [If any specific names (Rahul Sanghi, Vishesh Rajaram) appear in text, list their take here. Otherwise, list 'No major signal from tracked accounts today'.]
"""

OUTPUT_DIR = "content"
DB_NAME = "news_memory.db"