import feedparser
import asyncio
import random
import time
import requests
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
        """Fetches RSS feeds (Headlines only)."""
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
                
                if not feed.entries:
                    print(f"      ⚠️ Parsed 0 entries for {src['name']}")
                    continue
                
                print(f"      ✅ Found {len(feed.entries)} items.")
                
                # Take top 3 only
                for entry in feed.entries[:3]:
                    results.append({
                        "source": src['name'],
                        "title": entry.title,
                        "url": entry.link,
                        "content": getattr(entry, 'summary', ''),
                        "type": "rss_headline" # Mark as headline so we know to enrich it later
                    })
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
                
        return results

    async def fetch_sites(self, sources):
        """Scrapes entire sites (already Full Text)."""
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
                        results.append({
                            "source": src['name'],
                            "title": f"Scrape of {src['name']}",
                            "url": src['url'],
                            "content": result.markdown[:15000],
                            "type": "scrape"
                        })
                except Exception as e:
                    print(f"      ❌ Scrape Error {src['name']}: {e}")
        return results

    async def enrich_with_full_text(self, items):
        """
        Takes a list of RSS headlines, visits the links, and gets the FULL text.
        This is how you get the 'Deep Tech' details (Pricing, Specs).
        """
        print("🕵️ DEEP READ: Visiting top stories for details...")
        enriched_items = []
        
        # Only deep scrape the top 5 items total to save time/bandwidth
        # You can increase this number if you want more depth
        targets = items[:5] 
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for item in targets:
                if item['type'] == 'scrape': 
                    enriched_items.append(item)
                    continue

                print(f"   📖 Reading full article: {item['title'][:30]}...")
                try:
                    time.sleep(1) # Be polite
                    result = await crawler.arun(url=item['url'], config=self.run_config)
                    
                    if result.success and len(result.markdown) > 500:
                        # Replace the short RSS summary with the full article text
                        item['content'] = result.markdown[:15000] 
                        item['type'] = 'full_article'
                        print(f"      ✅ Captured {len(item['content'])} chars.")
                    else:
                        print(f"      ⚠️ Could not read full text (using summary).")
                except Exception as e:
                    print(f"      ❌ Failed to read: {e}")
                
                enriched_items.append(item)
        
        # Add back the rest of the items (headlines only)
        enriched_items.extend(items[5:])
        return enriched_items