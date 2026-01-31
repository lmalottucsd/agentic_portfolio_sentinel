import yfinance as yf
from typing import Dict, Any

class MetadataFetcher:
    def __init__(self):
        self.cache = {}

    def get_metadata(self, ticker_symbol: str) -> Dict[str, str]:
        """
        Fetches metadata for a given ticker:
        - name: Long company name (e.g. JPMorgan Chase & Co.)
        - ceo: Name of the CEO
        - sector: Sector name
        """
        if ticker_symbol in self.cache:
            return self.cache[ticker_symbol]

        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            # Extract CEO
            ceo = "CEO" # Fallback
            for officer in info.get("companyOfficers", []):
                title = officer.get("title", "").upper()
                if "CEO" in title or "CHIEF EXECUTIVE OFFICER" in title:
                    ceo = officer.get("name")
                    break
            
            metadata = {
                "name": info.get("longName", ticker_symbol),
                "sector": info.get("sector", "Business"),
                "ceo": ceo
            }
            self.cache[ticker_symbol] = metadata
            return metadata
        except Exception as e:
            print(f"Error fetching metadata for {ticker_symbol}: {e}")
            return {
                "name": ticker_symbol,
                "sector": "Business",
                "ceo": "CEO"
            }
