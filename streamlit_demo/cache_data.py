import json
import os
import yfinance as yf
import pandas as pd

DATA_PATH = os.path.join("data", "scout_latest.json")

def cache_prices():
    print(f"Reading from {DATA_PATH}...")
    if not os.path.exists(DATA_PATH):
        print("Error: scout_latest.json not found.")
        return

    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    holdings = data.get("data", {}).get("holdings", {}).keys()
    print(f"Found tickers: {list(holdings)}")

    for ticker in holdings:
        print(f"Fetching data for {ticker}...")
        try:
            # Fetch 6 months of data
            df = yf.download(ticker, period="6mo", interval="1d", progress=False)
            
            # Normalize structure
            if isinstance(df.columns, pd.MultiIndex):
                try:
                    df = df['Close']
                except:
                    df = df.iloc[:, 0]
            elif 'Close' in df.columns:
                df = df['Close']
            
            # Reset index to make date a column
            df = df.reset_index()
            # Convert timestamp to string
            df['Date'] = df['Date'].astype(str)
            
            # Save to JSON
            out_file = os.path.join("data", f"prices_{ticker}.json")
            # Convert to records: [{"Date": "2023-01-01", "JPM": 150.0}, ...] or similar
            # Since yfinance output varies, let's just save the simple date/price mapped records
            
            # Clean column names (sometimes it's "Close", sometimes "JPM")
            # We just want the numeric column that isn't Date
            price_col = [c for c in df.columns if c != "Date"][0]
            
            records = []
            for _, row in df.iterrows():
                records.append({
                    "Date": row["Date"],
                    "Price": row[price_col]
                })

            with open(out_file, "w") as f_out:
                json.dump(records, f_out, indent=2)
            
            print(f"Saved {out_file}")
            
        except Exception as e:
            print(f"Failed to fetch {ticker}: {e}")

if __name__ == "__main__":
    # Ensure we run from the script's directory or handle paths relative to it
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    cache_prices()
