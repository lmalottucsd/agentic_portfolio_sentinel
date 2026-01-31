import streamlit as st
import json
import os
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="Agentic Sentinel - Mitigating Risk",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Data
DATA_PATH = os.path.join("data", "scout_latest.json")

def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    with open(DATA_PATH, "r") as f:
        return json.load(f)

raw_data = load_data()

# Robustly handle data structure changes
data_payload = {}
timestamp = "Unknown"
if raw_data:
    # Check if new structure (has 'data' key) or old structure
    if "data" in raw_data:
        data_payload = raw_data["data"]
        timestamp = raw_data.get("timestamp")
    else:
        # Fallback for old structure (though we should re-run scout)
        st.error("Data format outdated. Please run the Scout agent.")
        st.stop()

# Sidebar
with st.sidebar:
    st.header("Risk Navigator")
    st.info("Agentic Mode: Active")
    if timestamp:
        st.caption(f"Last Scan: {timestamp}")
    
    st.divider()
    st.write("### Stocks in Portfolio:")
    holdings = data_payload.get("holdings", {}).keys()
    if holdings:
        st.caption(f"Monitoring: {', '.join(holdings)}")
    else:
        st.caption("No holdings detected.")

    st.divider()
    if st.button("Refresh Data"):
        st.rerun()

# Main Content
current_date = datetime.now().strftime("%Y-%m-%d")
st.title(f"The Sentinel's Weekly Briefing ({current_date})")

if not data_payload or not data_payload.get("holdings"):
    st.warning("No Scan Data Found. Run the 'Scout' agent first.")
    st.stop()

# TABS for each company
tickers = list(data_payload["holdings"].keys())
tabs = st.tabs(tickers)

for i, ticker in enumerate(tickers):
    with tabs[i]:
        company_data = data_payload["holdings"][ticker]
        
        


        # 0. Live Chart (The Situation Now)
        try:
            import yfinance as yf
            import pandas as pd
            # Fetch last 6 months
            st.caption("**Everything that happened since the last briefing, summarized:**")
            df_curr = yf.download(ticker, period="6m", interval="1d", progress=False)
            if not df_curr.empty:
                # Handle MultiIndex if present
                if isinstance(df_curr.columns, pd.MultiIndex):
                    # yfinance returns (Price, Ticker) levels sometimes
                    try:
                        df_curr = df_curr['Close']
                    except:
                        df_curr = df_curr.iloc[:, 0] # Fallback to first column
                elif 'Close' in df_curr.columns:
                     df_curr = df_curr['Close']
                
                st.line_chart(df_curr, color="#00FF00") # Green for current
        except Exception as e:
            st.warning(f"Could not load live chart: {e}")


        summary_text = company_data.get("summary", "No summary available.")
        # Sanitize text to remove markdown code ticks that cause font mismatches
        summary_text = summary_text.replace("`", "")
        st.info(summary_text) 
        
        # 1.5 Historical Context (The Historian)
        hist_contexts = company_data.get("historical_context") 
        
        if hist_contexts and isinstance(hist_contexts, list) and len(hist_contexts) > 0:
            st.markdown("### Historical Parallels (Top 3 Matches)")
            
            # Create tabs for the matches
            match_names = [ctx['archetype']['name'].split("(")[0].strip() for ctx in hist_contexts]
            # Handle potential duplicate names
            match_names = [f"{name} ({ctx['archetype']['ticker']})" for name, ctx in zip(match_names, hist_contexts)]
            
            hist_tabs = st.tabs(match_names)
            
            for idx, ctx in enumerate(hist_contexts):
                with hist_tabs[idx]:
                    archetype = ctx.get("archetype", {})
                    perf = ctx.get("performance", {})
                    
                    with st.container(border=True):
                        col_h1, col_h2 = st.columns([2, 1])
                        with col_h1:
                            st.markdown(f"**Archetype:** {archetype.get('name')}")
                            st.caption(f"Semantic Distance: {archetype.get('distance'):.4f}")
                            st.write(f"*{archetype.get('historical_summary')}*")
                        with col_h2:
                            if "error" in perf:
                                st.error(f"Data Error: {perf.get('error')}")
                            else:
                                ret = perf.get('total_return_pct')
                                dd = perf.get('max_drawdown_pct')
                                st.metric("Historical Return", f"{ret}%", delta=f"{ret}%")
                                st.metric("Max Drawdown", f"{dd}%", delta=f"{dd}%")
                    
                    # Chart the historical drawdown
                    ts_data = perf.get("timeseries", [])
                    if ts_data:
                        import pandas as pd
                        df_hist = pd.DataFrame(ts_data)
                        df_hist['date'] = pd.to_datetime(df_hist['date'])
                        df_hist = df_hist.set_index('date')
                        
                        # Chart name
                        ticker_label = archetype.get('ticker') or archetype.get('id')
                        st.caption(f"**The Ghost of Risk Past**: {ticker_label} Price Action (Normalized to 100)")
                        st.line_chart(df_hist['normalized'], color="#FF4B4B")  # Red for risk

        
        st.divider()
        
        # 2. Ranked Event Feed
        st.subheader(f"{ticker} News Feed, Listed by Relevance")
        
        events = company_data.get("events", [])
        if not events:
            st.write("No significant events detected.")
        else:
            for event in events:
                reason = event.get('reason', '').replace("`", "")
                title = event.get('title', '').replace("`", "")
                snippet = event.get('snippet', 'No snippet').replace("`", "")
                
                # Default expander, no score prefix
                with st.expander(f"{title}", expanded=False):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**Snippet:** {snippet}")
                        # Hide "Why this matters" if irrelevant/unavailable
                        if reason and "LLM unavailable" not in reason:
                            st.caption(f"**Why this matters:** {reason}")
                    with col_b:
                        st.caption(f"Source: {event.get('source', 'Unknown')}")
                        st.caption(f"Date: {event.get('published_date', 'Unknown')}")
                        st.markdown(f"[Read Article]({event.get('url')})")

        st.divider()

        # 4. Strategic Risk Assessment (The Advisor - Phase 4)
        advisor_report = company_data.get("advisor_report", {})
        if advisor_report:
            verdict = advisor_report.get("verdict", "Neutral")
            confidence = advisor_report.get("confidence", 0)
            
            # Color logic
            v_color = "red" if "Critical" in verdict else "orange" if "Elevated" in verdict or "High" in verdict else "green"
            
            st.markdown(f"### Strategic Risk Assessment: :{v_color}[{verdict}]")
            st.progress(confidence, text=f"Confidence Score: {confidence}%")
            
            st.info(f"**Synthesis:** {advisor_report.get('synthesis')}")
            
            with st.expander("Recommended Action Plan", expanded=True):
                for action in advisor_report.get("action_plan", []):
                    st.checkbox(action, key=f"{ticker}_{action}")




st.divider()
st.caption("Agentic Portfolio Risk Mitigation System | Powered by LPL Financial & Google SerpApi")
