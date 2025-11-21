import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() 

from src.config import RSS_SOURCES, SCRAPE_SOURCES, OUTPUT_DIR
from src.db import NewsMemory
from src.scraper import RobustScraper
from src.ai_agent import NewsEditor

async def main():
    print(f"🚀 Starting Deep Tech Engine | {datetime.now()}")
    
    db = NewsMemory()
    
    try:
        # 1. Initialize
        await db.init_db()
        scraper = RobustScraper()
        editor = NewsEditor()

        # 2. Gather Headlines (Fast)
        raw_rss = await scraper.fetch_rss(RSS_SOURCES)
        raw_site = await scraper.fetch_sites(SCRAPE_SOURCES)
        all_items = raw_rss + raw_site

        if not all_items:
            print("❌ No data collected.")
            return

        # 3. Filter Duplicates
        new_items = []
        print("🔍 Checking Memory (Deduplication)...")
        for item in all_items:
            if not await db.is_duplicate(item['url']):
                new_items.append(item)
            else:
                print(f"   Skipping seen: {item['title'][:20]}...")

        if not new_items:
            print("😴 No new items. Exiting.")
            return

        # 4. DEEP READ (The New Step)
        # We visit the links of the new items to get pricing, specs, and real info.
        print(f"⚡ Found {len(new_items)} new items. Starting Deep Read...")
        deep_items = await scraper.enrich_with_full_text(new_items)

        # 5. Intelligence Processing
        print("🧠 AI: Writing analysis...")
        blog_content = editor.filter_and_rewrite(deep_items)

        # 6. Publish
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filename = f"{OUTPUT_DIR}/{datetime.now().strftime('%Y-%m-%d')}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Daily Intel: {datetime.now().strftime('%d %b %Y')}\n\n")
            f.write(blog_content)
        
        print(f"✅ Published: {filename}")

        # 7. Update Memory
        print("💾 Updating Memory...")
        for item in new_items:
            await db.add_news(item['url'], item['title'], item['source'])

    except Exception as e:
        print(f"🚨 FATAL ERROR: {e}")
    
    finally:
        print("🏁 Mission Complete.")

if __name__ == "__main__":
    asyncio.run(main())