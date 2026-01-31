from serpapi import GoogleSearch
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class SerpClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not found.")

    def search_news(self, query: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Searches Google News via SerpApi.
        
        Args:
            query: The search query.
            days_back: Freshness (e.g., 1 for 24h, 7 for week). 
                       Maps to 'qdr:d' or 'qdr:w'.
        """
        # Map days to Google's 'tbs' (time based search) parameter
        time_period = "qdr:w" # Default week
        if days_back <= 1:
            time_period = "qdr:d"
        elif days_back <= 30:
            time_period = "qdr:m"
            
        params = {
            "engine": "google",
            "tbm": "nws",
            "q": query,
            "tbs": time_period,
            "api_key": self.api_key,
            "gl": "us", # country
            "hl": "en"  # language
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            news_results = results.get("news_results", [])
            
            # Standardize output
            standardized = []
            for item in news_results:
                standardized.append({
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "snippet": item.get("snippet", "No snippet available"),
                    "source": item.get("source"),
                    "published_date": item.get("date")
                })
            return standardized
        except Exception as e:
            print(f"Error executing SerpApi search '{query}': {e}")
            return []
