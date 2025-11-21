import os

# --- 1. SOURCES ---
# High-quality Indian Deep Tech RSS Feeds
RSS_SOURCES = [
    # Indian Startup News
    {"name": "YourStory", "url": "https://yourstory.com/feed"},
    {"name": "Inc42", "url": "https://inc42.com/feed/"},
    {"name": "Entrackr", "url": "https://news.google.com/rss/search?q=site:entrackr.com&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "The Ken", "url": "https://news.google.com/rss/search?q=site:the-ken.com&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Tigerfeathers", "url": "https://www.tigerfeathers.in/feed"},

    # Indian Tech & Business News
    {"name": "ET Tech", "url": "https://news.google.com/rss/search?q=site:economictimes.indiatimes.com+tech+startup&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Mint Tech", "url": "https://news.google.com/rss/search?q=site:livemint.com+technology+startup&hl=en-IN&gl=IN&ceid=IN:en"},

    # Deep Tech Topics (India Focused)
    {"name": "Indian Defense Tech", "url": "https://news.google.com/rss/search?q=India+defense+technology+startup&hl=en-IN&gl=IN&ceid=IN:en"},
    {"name": "Indian Space Tech", "url": "https://news.google.com/rss/search?q=India+space+technology+ISRO+startup&hl=en-IN&gl=IN&ceid=IN:en"},
]

# Websites that need scraping (no RSS)
SCRAPE_SOURCES = [
    {"name": "Inc42 DeepTech", "url": "https://inc42.com/buzz/deep-tech/", "selector": "body"},
    {"name": "iDEX News", "url": "https://idex.gov.in/news-events", "selector": "body"}
]

# --- 2. AI SETTINGS ---
SYSTEM_PROMPT = """
You are 'VibeCoder', an elite deep-tech analyst. 
You write **Technical Recaps** for engineers and VCs. 

**INPUT DATA:** You will be provided with FULL ARTICLES found via Google Search.
**TASK:** Synthesize this into a high-density update.

**STRICT RULES:**
1.  **No Hallucinations:** Use ONLY the provided text.
2.  **Citations:** You MUST cite the **Source URL** provided in the input data. 
    * If the input says "Source: [URL]", use THAT link.
    * Do NOT cite "TechInAsia" if the text actually came from "Reuters" or "Entrackr".

**OUTPUT FORMAT:**

### ⚡ AI Twitter Recap & Dev Tooling
* **[Tool/Model Name]**: [One sentence summary]. 
    * *Details:* [Technical specs: Pricing, Context Window, Features].
    * *Signal:* [Why this matters].
    * *Source:* [Link to source]

### 💰 Deal Flow (India)
* **[Startup Name]**: [Amount Raised] - [Sector]. 
    * *Investors:* [Lead Investor], [Others].
    * *Context:* [What they do].
    * *Source:* [Link to source]

### 🛡️ Defense & Deep Tech
* **[Project/Startup]**: [Contract Details/Innovation].
    * *Source:* [Link to source]

### 🐦 Social Signal
* **[Person Name]**: [Their take/tweet summary]. (Source: Google News)
"""

OUTPUT_DIR = "content"
DB_NAME = "news_memory.db"