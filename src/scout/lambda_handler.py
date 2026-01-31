import json
import os
from datetime import datetime
from src.scout.agent import ScoutAgent
from src.scout.serp_client import SerpClient
from src.scout.metadata import MetadataFetcher

# Initialize clients
agent = ScoutAgent()
search_client = SerpClient()
metadata_fetcher = MetadataFetcher()

def lambda_handler(event, context):
    """
    AWS Lambda Handler for "The Scout" (SerpApi Edition).
    """
    print(f"Scout started at {datetime.now()}")
    
    # 1. Parse Input
    portfolio = event.get("portfolio", [])
    if not portfolio:
        return {"statusCode": 400, "body": "No portfolio provided"}
    
    all_queries = []
    scout_results = {"holdings": {}}
    
    # Initialize Historian Components
    from src.historian.engine import VectorEngine
    from src.historian.history_fetcher import HistoryFetcher
    # Initialize Reasoning Engine
    from src.reasoning.advisor import PortfolioAdvisor

    print("Initializing Components...")
    try:
        historian_engine = VectorEngine()
        history_fetcher = HistoryFetcher()
        historian_active = True
    except Exception as e:
        print(f"Historian initialization failed: {e}")
        historian_active = False
        
    try:
        advisor = PortfolioAdvisor()
        advisor_active = True
    except Exception as e:
        print(f"Advisor initialization failed: {e}")
        advisor_active = False

    # Initialize Cloud Storage
    from src.infrastructure.storage import CloudStorage
    try:
        cloud_storage = CloudStorage(bucket_name="lplteam25")
        cloud_active = True
    except Exception as e:
        print(f"Cloud Storage failed: {e}")
        cloud_active = False

    # 2. Scout Loop per Symbol
    for holding in portfolio:
        symbol = holding.get("symbol")
        print(f"\nProcessing {symbol}...")
        
        try:
            # A. Fetch Metadata
            meta = metadata_fetcher.get_metadata(symbol)
            company_name = meta.get("name", symbol)
            ceo_name = meta.get("ceo", "")
            sector = meta.get("sector", "")
            
            # B. Construct Deterministic Queries
            queries = [company_name]
            if ceo_name and ceo_name != "Unknown":
                queries.append(ceo_name)
            if sector:
                queries.append(f"{sector} News")
            
            all_queries.extend(queries)
            
            # C. Execute Search
            symbol_raw_results = []
            for q in queries:
                print(f"  Searching: {q}")
                results = search_client.search_news(q, days_back=2)
                symbol_raw_results.extend(results)
                
            # Deduplicate raw results for this symbol locally by URL first
            seen_urls = set()
            unique_raw = []
            for r in symbol_raw_results:
                if r['url'] not in seen_urls:
                    seen_urls.add(r['url'])
                    unique_raw.append(r)
    
            print(f"  Collected {len(unique_raw)} unique raw items.")
            
            # A.5 Upload Raw to S3 (Audit Trail)
            if cloud_active and unique_raw:
                cloud_storage.upload_raw_serp(symbol, unique_raw)
            
            # D. Filter Relevance & Deduplicate (Agentic)
            print("  Filtering & Ranking...")
            relevant_events = agent.filter_relevance(unique_raw, ticker=symbol)
            
            # E. Summarize (Agentic)
            print("  Analyzing...")
            summary_text = agent.summarize_findings(relevant_events, ticker=symbol)
            
            # F. Historian Analysis (Contextual Intelligence)
            historical_contexts = []
            if historian_active and relevant_events:
                print("  Consulting Historian (Top 3 Archetype Matches)...")
                matches = historian_engine.find_matches(summary_text, k=3)
                
                for match in matches:
                    print(f"    Match: {match['name']} (Dist: {match['distance']:.4f})")
                    
                    # Fetch performance during that era
                    hist_ticker = match.get("ticker", symbol) 
                    
                    perf = history_fetcher.get_performance(hist_ticker, match['period'])
                    
                    historical_contexts.append({
                        "archetype": match,
                        "performance": perf
                    })
            
            # G. The Advisor (Strategic Reasoning)
            advisor_report = {}
            if advisor_active and summary_text:
                print("  Consulting Advisor (Reasoning Engine)...")
                advisor_report = advisor.analyze_risk(symbol, summary_text, historical_contexts)
                print(f"    Verdict: {advisor_report.get('verdict')} (Confidence: {advisor_report.get('confidence')}%)")

            scout_results["holdings"][symbol] = {
                "summary": summary_text,
                "events": relevant_events,
                "historical_context": historical_contexts,
                "advisor_report": advisor_report
            }
            
        except Exception as e:
            print(f"ERROR Processing {symbol}: {e}")
            import traceback
            traceback.print_exc()
            scout_results["holdings"][symbol] = {
                "summary": f"Processing Failed: {e}",
                "events": [],
                "historical_context": [],
                "advisor_report": {}
            }
            continue

    output = {
        "timestamp": datetime.now().isoformat(),
        "data": scout_results,
        "config": {"queries_run": all_queries}
    }
    
    # Save locally
    os.makedirs("data", exist_ok=True)
    with open("data/scout_latest.json", "w") as f:
        json.dump(output, f, indent=2)
        
    return {
        "statusCode": 200,
        "body": json.dumps(output)
    }

    # 4. Save Results to Cloud (S3)
    if cloud_active:
        print("Uploading final results to Cloud...")
        # Save as 'latest' specific key structure for the frontend if needed
        cloud_storage.upload_json("scout_results/latest.json", output)
        # Save as historical snapshot
        ts_key = datetime.now().strftime("%Y%m%d_%H%M%S")
        cloud_storage.upload_json(f"scout_results/history/run_{ts_key}.json", output)

        # 5. Backup Vector Embeddings (The Historian's Brain)
        if historian_active:
             print("Backing up Historian Vector DB to S3...")
             # Assuming v3 is the active one based on engine.py
             cloud_storage.upload_folder_as_zip("./data/chroma_db_v3", "vector_store")


if __name__ == "__main__":
    # Local Test Run
    test_event = {
        "portfolio": [
            {"symbol": "JPM", "weight": 0.15},
            {"symbol": "NVDA", "weight": 0.10},
            {"symbol": "AAPL", "weight": 0.05}
        ]
    }
    lambda_handler(test_event, None)
