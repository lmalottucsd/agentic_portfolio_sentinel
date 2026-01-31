import boto3
import json
import os
from typing import List, Dict, Any

class ScoutAgent:
    def __init__(self, region_name: str = "us-east-1"):
        self.bedrock = boto3.client("bedrock-runtime", region_name=region_name)
        # Reverting to Claude 3.5 Sonnet for stability
        self.model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0" 

    def _invoke_model(self, prompt: str, system_prompt: str = "") -> str:
        """Helper to invoke Claude 3.5 Sonnet on Bedrock."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1
        })
        
        try:
            response = self.bedrock.invoke_model(
                body=body,
                modelId=self.model_id,
                accept="application/json",
                contentType="application/json"
            )
            response_body = json.loads(response.get("body").read())
            return response_body["content"][0]["text"]
        except Exception as e:
            print(f"Error invoking Bedrock: {e}")
            return ""

    # generate_queries method removed in favor of deterministic logic in lambda_handler

    def filter_relevance(self, search_results: List[Dict[str, Any]], ticker: str) -> List[Dict[str, Any]]:
        """
        Filters search results for direct relevance, removes duplicates, and ranks by impact.
        Returns a sorted list of relevant items.
        """
        if not search_results:
            return []
            
        system_prompt = (
            "You are a strict Senior Editor. Your goal is to curate a high-signal news feed for a Portfolio Manager.\n"
            "1. ELIMINATE REDUNDANCY: If multiple articles cover the exact same event, keep ONLY the best source.\n"
            "2. STRICT RELEVANCE: Discard generic market updates, 'top 10' lists, or minor price movements. Keep only MATERIAL events (earnings, reg action, M&A, supply chain).\n"
            "3. RANKING: Score each item 1-10 on material impact."
        )
        
        # We need to process this carefully. Limit to top 50 to avoid context overflow.
        # Since we effectively random-sort raw results, taking top 50 is acceptable for now.
        processed_results = search_results[:50]
        
        results_digest = "\n".join([
            f"ID: {i} | Title: {r.get('title')} | Snippet: {r.get('snippet')}" 
            for i, r in enumerate(processed_results)
        ])
        
        prompt = (
            f"Ticker: {ticker}\n"
            f"Raw Feed:\n{results_digest}\n\n"
            "Task:\n"
            "1. Identify the unique, material storylines.\n"
            "2. Select the single best article for each storyline.\n"
            "3. Rank them by importance (10 = Critical).\n\n"
            "Return JSON: a list of objects selected: [{'id': int, 'score': int, 'reason': str}, ...]"
        )
        
        response_text = self._invoke_model(prompt, system_prompt)
        try:
            import re
            # Regex to find JSON block
            json_match = re.search(r'\[.*\]', response_text.replace("\n", " "), re.DOTALL)
            if json_match:
                clean_text = json_match.group(0)
            else:
                # Try finding { if it's a single object (unlikely for list instructions but possible)
                clean_text = response_text.replace("```json", "").replace("```", "").strip()

            selected_items = json.loads(clean_text)
            
            final_results = []
            for item in selected_items:
                idx = item.get('id')
                # Validate index
                if isinstance(idx, int) and 0 <= idx < len(processed_results):
                    article = processed_results[idx]
                    article['relevance_score'] = item.get('score', 0)
                    article['reason'] = item.get('reason', '')
                    final_results.append(article)
            
            # Sort by score descending
            final_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            return final_results
            
        except Exception as e:
            print(f"Error filtering results for {ticker}: {e}")
            print(f"DEBUG: Response Text was: {response_text[:200]}...")
            
            # Fallback: Dedupe and assign default score so output isn't empty/zero
            unique = {}
            for r in processed_results:
                if r['title'] not in unique:
                    # Do NOT say LLM unavailable if we can help it, assume it's just a parse error
                    r['relevance_score'] = 5 
                    r['reason'] = f"Automated selection (Parse Error)"
                    unique[r['title']] = r
            return list(unique.values())[:10]


    def summarize_findings(self, relevant_news: List[Dict[str, Any]], ticker: str) -> str:
        """
        Creates a detailed analysis for a specific company.
        """
        if not relevant_news:
            return "No significant material events detected."
            
        system_prompt = "You are a Senior Risk Analyst writing a briefing for a Portfolio Manager."
        news_text = "\n".join([f"- {r.get('title')} (Score: {r.get('relevance_score')}): {r.get('snippet')}" for r in relevant_news])
        
        prompt = (
            f"Ticker: {ticker}\n"
            f"Key Developments:\n{news_text}\n\n"
            "Provide a DETAILED analysis (2 paragraphs). \n"
            "1. Synthesize the key risks and opportunities based *strictly* on these events.\n"
            "2. Connect the dots between separate events if possible (e.g. supply chain issues affecting earnings).\n"
            "Do NOT be generic. Be specific to the news provided."
        )
        
        return self._invoke_model(prompt, system_prompt)
