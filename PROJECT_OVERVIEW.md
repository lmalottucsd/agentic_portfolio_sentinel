# Agentic Portfolio Risk Mitigation - System Overview

## 1. General Overhead (What the Code Does)
This system is an autonomous "Risk Intelligence" pipeline designed to monitor portfolio assets (e.g., JPM, NVDA, AAPL) for semantic risks that traditional algos might miss. It operates in three distinct phases:

1.  **Phase 1: The Scout (Eyes)**
    - actively searches the web for *specific* news about company management, sector trends, and legal issues.
    - Filters out noise (generic market reports) using an LLM.
    - Ranks events by "Material Impact".

2.  **Phase 2: The Historian (Memory)**
    - Maintains a Vector Database of historical market crashes and risk events (e.g., "Dotcom Bubble", "2008 Financial Crisis").
    - "Semantic Search" compares today's news summaries against these historical archetypes to find dangerous parallels (e.g., "Is Nvidia's current hype similar to Cisco in 2000?").

3.  **Phase 3: The Advisor (Brain)**
    - A "Chief Risk Officer" agent synthesizes the conflicting signals from the Scout (News) and Historian (Past).
    - Produces a final strategic verdict (Critical/Elevated/Neutral) and an actionable checklist.

## 2. APIs & External Services
The system relies on the following external data sources:

*   **Google SerpAPI**: Used by the Scout to perform real-time, targeted web searches for news and press releases.
*   **Yahoo Finance (`yfinance`)**: Used to fetch:
    *   Live 6-month price charts for context.
    *   Deep historical price data (daily candlesticks) to reconstruct the "Price Action" of historical archetypes (e.g., retrieving MSFT price data from 1999).
*   **AWS Bedrock Runtime**: The interface for invoking the Large Language Models.

## 3. AWS Tools & Infrastructure
The system is "Cloud-Native" ready but currently runs locally with Cloud bindings.

*   **AWS Bedrock (Generative AI)**
    *   **Model**: `anthropic.claude-3-5-sonnet-20240620-v1:0`
    *   **Usage**:
        *   Filtering irrelevant news.
        *   Summarizing complex legal/financial events.
        *   Generating the "Strategic Risk Assessment" and "Action Plan".
*   **AWS S3 (Simple Storage Service)**
    *   **Bucket**: `lplteam25`
    *   **Usage**:
        *   **Audit Trail**: Stores raw, unfiltered JSON search results (`/raw_scans/`) for compliance/debugging.
        *   **Persistence**: Stores the final processed analysis (`/scout_results/`).
        *   **Backup**: Stores zipped snapshots of the Vector Database (`/vector_store/`) to preserve the "Historian's Memory".

## 4. Storage Architecture
Data is managed in two layers:

### A. Local (Ephemeral/Fast Access)
*   `./data/chroma_db_v3/`: The **ChromaDB** vector store containing embeddings of historical events.
*   `./data/scout_latest.json`: The most recent run's output, used by the Dashboard for fast loading.

### B. Cloud (Permanent/Audit)
*   `s3://lplteam25/raw_scans/{YYYY-MM-DD}/{ticker}_{timestamp}.json`: Raw search evidence.
*   `s3://lplteam25/scout_results/latest.json`: The "Source of Truth" for the latest analysis.
*   `s3://lplteam25/vector_store/chroma_backup_{timestamp}.zip`: Disaster recovery for the semantic memory.

## 5. Key Python Libraries
*   `streamlit`: The interactive dashboard UI.
*   `boto3`: AWS SDK for Python (S3 & Bedrock).
*   `chromadb`: The open-source embedding database for the Historian.
*   `pandas`: Time-series data manipulation.
