import os
import json
from typing import List, Dict, Any
from parallel import Parallel
from dotenv import load_dotenv

load_dotenv()

class ParallelClient:
    def __init__(self, api_key: str = None):
        search_api_key = api_key or os.getenv("PARALLEL_API_KEY")
        if not search_api_key:
            raise ValueError("PARALLEL_API_KEY not found in environment variables or passed as argument.")
        
        self.client = Parallel(api_key=search_api_key)

    def search(self, query: str, num_results: int = 5, days_back: int = 2) -> List[Dict[str, Any]]:
        """
        Executes a search query using Parallel AI Search with date filtering.
        
        Args:
            query (str): The search query string.
            num_results (int): Number of results to return.
            days_back (int): How many days back to search (default 2 for 48h freshness).
            
        Returns:
            List[Dict[str, Any]]: A list of search results with 'title', 'url', 'snippet'.
        """
        # Calculate date threshold for "fresh" news
        # Parallel API requires YYYY-MM-DD format for 'after_date'
        from datetime import datetime, timedelta
        date_threshold = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        try:
            # Using the identified method: client.beta.search(search_queries=[query], source_policy=...)
            # We strictly filter for news published AFTER the threshold date.
            response = self.client.beta.search(
                search_queries=[query],
                source_policy={"after_date": date_threshold}
            )
            
            # Normalize response to a standard list of dicts
            results = []
            if isinstance(response, dict):
                 # Handle if response is wrapped
                 items = response.get("results", [])
            elif isinstance(response, list):
                items = response
            # Check if response acts like a list (some API objects do)
            elif hasattr(response, "results"):
                 items = response.results
            else:
                 # It might be an object, try to iterate or convert
                 items = response

            for item in items:
                # Different APIs structure return differently. We try to standardize.
                # Assuming item is dict-like or object with attributes
                if isinstance(item, dict):
                    results.append({
                        "title": item.get("title", "No Title"),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", item.get("snippet", "")),
                        "published_date": item.get("published_date", "")
                    })
                else:
                     # Fallback for object access if SDK returns objects
                     results.append({
                        "title": getattr(item, "title", "No Title"),
                        "url": getattr(item, "url", ""),
                        "snippet": getattr(item, "content", getattr(item, "snippet", "")),
                        "published_date": getattr(item, "published_date", "")
                    })

            return results
        except Exception as e:
            print(f"Error executing Parallel search '{query}': {e}")
            return []

if __name__ == "__main__":
    # Quick Test
    try:
        client = ParallelClient()
        print("Testing Parallel Search...")
        results = client.search("latest risks for Apple stock 2024")
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Test Failed: {e}")
