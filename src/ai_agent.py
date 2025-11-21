import google.generativeai as genai
import os
from src.config import SYSTEM_PROMPT

class NewsEditor:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY is missing!")
        
        genai.configure(api_key=api_key)
        
        # FIX: Updated to 2025 Stable Model
        # 'gemini-1.5-flash' is retired. We use 2.5.
        self.model_name = 'gemini-2.5-flash' 
        self.model = genai.GenerativeModel(self.model_name)

    def filter_and_rewrite(self, raw_news_items):
        if not raw_news_items:
            return "No significant news found today."

        data_block = ""
        for item in raw_news_items:
            # Truncate to avoid token limits
            content_preview = item['content'][:3000] if item['content'] else "No content."
            data_block += f"--- SOURCE: {item['source']} ---\n"
            data_block += f"LINK: {item['url']}\n"
            data_block += f"CONTENT: {content_preview}\n\n"

        try:
            print(f"🧠 AI: Analyzing with {self.model_name}...")
            response = self.model.generate_content(
                f"{SYSTEM_PROMPT}\n\nRAW DATA TO PROCESS:\n{data_block}"
            )
            return response.text
        except Exception as e:
            print(f"❌ AI Error: {e}")
            return f"Error generating digest. AI Error: {e}"