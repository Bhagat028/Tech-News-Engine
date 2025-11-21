import os
import libsql_client
import asyncio
from datetime import datetime

class NewsMemory:
    def __init__(self):
        self.url = os.environ.get("TURSO_DB_URL")
        self.token = os.environ.get("TURSO_AUTH_TOKEN")
        
        if not self.url:
            print("⚠️ No Turso keys found. Using local file.")
            self.url = "file:local_memory.db"
            self.token = None
        else:
            self.url = self.url.replace("libsql://", "https://")

    def get_client(self):
        return libsql_client.create_client(url=self.url, auth_token=self.token)

    async def init_db(self):
        """Creates the table if it doesn't exist."""
        client = self.get_client()
        try:
            # MUST HAVE AWAIT HERE
            await client.execute("""
                CREATE TABLE IF NOT EXISTS seen_news (
                    url TEXT PRIMARY KEY,
                    title TEXT,
                    source TEXT,
                    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Memory (DB) initialized.")
        except Exception as e:
            print(f"❌ DB Init Error: {e}")
        finally:
            await client.close()

    async def is_duplicate(self, url):
        """Checks if URL was already processed."""
        client = self.get_client()
        try:
            # MUST HAVE AWAIT HERE
            result = await client.execute("SELECT 1 FROM seen_news WHERE url = ?", [url])
            return len(result.rows) > 0
        except Exception as e:
            print(f"⚠️ DB Check Error: {e}")
            return False 
        finally:
            await client.close()

    async def add_news(self, url, title, source):
        """Saves URL to memory."""
        client = self.get_client()
        try:
            # MUST HAVE AWAIT HERE
            await client.execute(
                "INSERT INTO seen_news (url, title, source) VALUES (?, ?, ?)", 
                [url, title, source]
            )
        except Exception as e:
            print(f"⚠️ DB Save Error: {e}")
        finally:
            await client.close()