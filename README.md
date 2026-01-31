# Agentic Sentinel: Portfolio Risk Mitigation

An autonomous "Risk Intelligence" agent that monitors portfolio assets, compares them to historical market crashes, and generates strategic risk assessments.

![Dashboard Preview](dashboard_preview.png)

## What It Does
1.  **The Scout (Eyes)**: Searches the web (via SerpApi) for material news about your holdings (e.g., "CEO selling shares", "Regulatory probe").
2.  **The Historian (Memory)**: Uses a Vector Database (ChromaDB) to compare today's news against 5+ major historical market events (e.g., Dotcom Bubble, 2008 Crisis).
3.  **The Advisor (Brain)**: An LLM-based "Chief Risk Officer" synthesizes the news and history to output a strategic verdict (Red/Yellow/Green) and an action plan.

## Setup Requirements

### 1. APIs
You will need the following API keys:
*   **Google SerpApi**: For web searching. [Get Key](https://serpapi.com/)
*   **AWS Bedrock**: For the AI reasoning engine (Claude 3.5 Sonnet).

### 2. Installation
1.  Clone this repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up environment variables. Create a `.env` file in the root:
    ```ini
    SERPAPI_API_KEY=your_serpapi_key_here
    ```
    *Note: AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) should be set via the AWS CLI (`aws configure`) or environment variables.*

## How to Run
1.  **Run the Scout** (The Agent):
    This script runs the analysis pipeline. It searches news, consults history, and saves the results.
    ```bash
    python src/scout/lambda_handler.py
    ```

2.  **View the Dashboard**:
    This launches the interactive UI to view the results.
    ```bash
    streamlit run src/dashboard/app.py
    ```

## Architecture
*   **Data**: Results are saved locally to `./data/scout_latest.json` (also supports AWS S3 upload if configured).
*   **Vector DB**: Historical embeddings are stored in `./data/chroma_db_v3`.

## License
MIT
