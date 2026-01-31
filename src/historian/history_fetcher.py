import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

class HistoryFetcher:
    def __init__(self):
        pass

    def get_performance(self, ticker: str, period_str: str) -> Dict[str, Any]:
        """
        Fetches historical performance for a ticker during a specific period.
        period_str format: "YYYY-MM-DD_to_YYYY-MM-DD"
        """
        try:
            start_str, end_str = period_str.split("_to_")
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
            
            # Fetch data (buffer by a few days to ensure we get start price)
            df = yf.download(
                ticker, 
                start=start_date - timedelta(days=5), 
                end=end_date + timedelta(days=5),
                progress=False
            )
            
            if df.empty:
                return {"error": "No data found"}
                
            # Filter exactly to range
            mask = (df.index >= start_date) & (df.index <= end_date)
            period_df = df.loc[mask]
            
            if period_df.empty:
                return {"error": "No data in exact range"}
                
            # Calculate stats
            # Handle MultiIndex columns if present (yfinance update)
            adj_close = period_df['Adj Close'] if 'Adj Close' in period_df.columns else period_df['Close']
            
            # If multi-index (Ticker as column level), flatten or select
            if isinstance(adj_close, pd.DataFrame):
                 adj_close = adj_close.iloc[:, 0] # Take first column
            
            start_price = float(adj_close.iloc[0])
            end_price = float(adj_close.iloc[-1])
            min_price = float(adj_close.min())
            
            # Calculate Drawdown (Max decline from start)
            # Simple definition: (Min Price during period - Start Price) / Start Price
            # Or strict Max Drawdown (Peak to Trough). Let's use strict MDD.
            # Calculate running max
            rolling_max = adj_close.cummax()
            drawdown = (adj_close - rolling_max) / rolling_max
            max_drawdown_pct = float(drawdown.min()) * 100
            
            total_return_pct = ((end_price - start_price) / start_price) * 100
            
            # Create a normalized time series (Base 100) for easier plotting
            # JSON serialization requires strings for dates
            timeseries = []
            for date, price in adj_close.items():
                price_val = float(price)
                norm_val = 100 * (price_val / start_price)
                timeseries.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "price": round(price_val, 2),
                    "normalized": round(norm_val, 2)
                })
            
            return {
                "start_date": start_str,
                "end_date": end_str,
                "start_price": round(start_price, 2),
                "end_price": round(end_price, 2),
                "total_return_pct": round(total_return_pct, 2),
                "max_drawdown_pct": round(max_drawdown_pct, 2),
                "timeseries": timeseries
            }
            
        except Exception as e:
            print(f"Error fetching history for {ticker}: {e}")
            return {"error": str(e)}
