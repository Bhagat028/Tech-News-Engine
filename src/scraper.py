import feedparser
import asyncio
import random
import time
import requests
from urllib.parse import quote_plus
from googlesearch import search 
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

class RobustScraper:
    def __init__(self):
        self.browser_config = BrowserConfig(
            enable_stealth=True,
            headless=True,
            user_agent_mode="random"
        )
        self.run_config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            delay_before_return_html=2.0
        )
        self.rss_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*'
        }

    async def fetch_rss(self, sources):
        """Fetches RSS feeds using requests."""
        results = []
        print("📡 RSS: Starting fetch sequence...")
        for src in sources:
            try:
                print(f"   👉 Fetching {src['name']}...")
                response = requests.get(src['url'], headers=self.rss_headers, timeout=15)
                if response.status_code != 200:
                    print(f"      ❌ Status {response.status_code} for {src['name']}")
                    continue

                feed = feedparser.parse(response.content)
                if not feed.entries: continue
                
                print(f"      ✅ Found {len(feed.entries)} items.")
                for entry in feed.entries[:3]:
                    results.append({
                        "source": src['name'],
                        "title": entry.title,
                        "url": entry.link,
                        "content": getattr(entry, 'summary', ''),
                        "type": "rss_headline"
                    })
            except Exception as e:
                print(f"      ❌ Error: {e}")
        return results

    async def fetch_techinasia(self):
        """
        Scrapes headlines from TechInAsia India page.
        TechInAsia curates news from other sources (YourStory, ET, Reuters, etc.)
        This extracts BOTH the headline AND the original source.
        """
        results = []
        url = "https://www.techinasia.com/news?category=india"
        print(f"🕷️ SCRAPE: Fetching TechInAsia Headlines...")

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            try:
                result = await crawler.arun(url=url, config=self.run_config)
                if not result.success: return results

                # Parse markdown for headlines and sources
                lines = result.markdown.split('\n')
                count = 0

                for i, line in enumerate(lines):
                    if count >= 5:  # Limit to top 5 headlines
                        break

                    # Look for markdown links (headlines)
                    if "[" in line and "](" in line and len(line) > 30:
                        # Extract title
                        title = line.split("](")[0].replace("[", "").replace("#", "").strip()
                        if len(title) < 20:  # Too short, probably not a headline
                            continue

                        # Try to extract source attribution from nearby lines
                        # TechInAsia often shows "via YourStory", "Source: ET", etc.
                        original_source = None
                        search_range = lines[max(0, i-2):min(len(lines), i+3)]  # Check nearby lines

                        for nearby_line in search_range:
                            lower = nearby_line.lower()
                            # Look for source indicators
                            if any(indicator in lower for indicator in ['via', 'source:', 'from']):
                                # Extract source name
                                for known_source in ['yourstory', 'economic times', 'reuters',
                                                     'entrackr', 'inc42', 'mint', 'the ken',
                                                     'business standard', 'livemint']:
                                    if known_source in lower:
                                        original_source = known_source
                                        break

                        results.append({
                            "source": "TechInAsia Curated",
                            "title": title,
                            "url": url,
                            "content": f"Headline from TechInAsia. Original source: {original_source or 'Unknown'}",
                            "type": "search_required",
                            "original_source": original_source  # NEW: Store original source
                        })
                        count += 1
                        print(f"      ✓ {title[:40]}... (via {original_source or 'Unknown'})")

            except Exception as e:
                print(f"      ❌ TechInAsia Error: {e}")
        return results

    async def google_search_enrich(self, items):
        """
        Intelligent search strategy:
        1. If we know the original source -> search "headline site:source.com"
        2. If unknown -> search "headline india startup tech"
        3. Scrape the best non-paywalled result
        """
        print("🕵️ DEEP SEARCH: Finding full articles...")
        enriched_items = []

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for item in items:
                # Skip items that don't need enrichment
                if item.get('type') not in ['search_required', 'rss_headline']:
                    enriched_items.append(item)
                    continue

                title = item['title'][:80]  # Limit query length
                original_source = item.get('original_source')

                # SMART QUERY CONSTRUCTION
                if original_source:
                    # We know the source! Target it directly
                    # Map source names to domains
                    source_map = {
                        'yourstory': 'yourstory.com',
                        'economic times': 'economictimes.indiatimes.com',
                        'entrackr': 'entrackr.com',
                        'inc42': 'inc42.com',
                        'mint': 'livemint.com',
                        'livemint': 'livemint.com',
                        'the ken': 'the-ken.com',
                        'reuters': 'reuters.com',
                        'business standard': 'business-standard.com'
                    }
                    domain = source_map.get(original_source.lower())
                    if domain:
                        query = f"{title} site:{domain}"
                        print(f"   🎯 Targeted Search: {title[:30]}... @ {domain}")
                    else:
                        query = f"{title} {original_source} india"
                        print(f"   🔍 Searching: {title[:30]}... via {original_source}")
                else:
                    # Generic search with Indian context
                    query = f"{title} india startup tech news"
                    print(f"   🔍 Searching: {title[:30]}...")

                try:
                    # Execute Google Search
                    search_results = list(search(query, num_results=5, lang="en"))

                    found_url = None
                    for url in search_results:
                        # Skip paywalled/junk sites
                        blocked_sites = ['techinasia.com', 'google.com', 'youtube.com',
                                         'facebook.com', 'twitter.com', 'linkedin.com']
                        if not any(blocked in url for blocked in blocked_sites):
                            found_url = url
                            break

                    if found_url:
                        print(f"      ➡️  Found: {found_url}")

                        # Scrape the article
                        time.sleep(1)  # Rate limiting
                        news_res = await crawler.arun(url=found_url, config=self.run_config)

                        if news_res.success:
                            item['content'] = f"**Source:** {found_url}\n\n" + news_res.markdown[:15000]
                            item['url'] = found_url
                            item['type'] = 'full_article'
                            print(f"      ✅ Scraped {len(news_res.markdown)} chars")
                        else:
                            item['content'] = f"Failed to scrape: {found_url}"
                            print(f"      ❌ Scrape failed")
                    else:
                        print("      ⚠️  No suitable source found")

                except Exception as e:
                    print(f"      ❌ Search Error: {e}")

                enriched_items.append(item)

        return enriched_items

    async def fetch_sites(self, sources):
        """Scrapes websites using Headless Browser."""
        results = []
        if not sources: return results

        print("🕷️ SCRAPE: Starting browser sequence...")
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for src in sources:
                try:
                    print(f"   👉 Crawling {src['name']}...")
                    time.sleep(random.uniform(2, 5))
                    result = await crawler.arun(url=src['url'], config=self.run_config)
                    
                    if result.success:
                        content_snippet = result.markdown[:15000]
                        results.append({
                            "source": src['name'],
                            "title": f"Scrape of {src['name']}",
                            "url": src['url'],
                            "content": content_snippet,
                            "type": "scrape"
                        })
                except Exception as e:
                    print(f"      ❌ Scrape Error {src['name']}: {e}")
        return results