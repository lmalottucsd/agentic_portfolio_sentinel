import boto3
import json
import re
from typing import List, Dict, Any

class PortfolioAdvisor:
    def __init__(self, region_name: str = "us-east-1"):
        self.bedrock = boto3.client("bedrock-runtime", region_name=region_name)
        self.model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    def _invoke_model(self, prompt: str, system_prompt: str = "") -> str:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        })
        try:
            response = self.bedrock.invoke_model(
                body=body, modelId=self.model_id, accept="application/json", contentType="application/json"
            )
            return json.loads(response.get("body").read())["content"][0]["text"]
        except Exception as e:
            print(f"Advisor Error: {e}")
            return ""

    def analyze_risk(self, ticker: str, scout_summary: str, historical_contexts: List[Dict]) -> Dict[str, Any]:
        """
        Synthesizes the news (Scout) and history (Historian) into a strategic verdict.
        """
        # 1. Format Historical Context for the Prompt
        history_text = ""
        for i, ctx in enumerate(historical_contexts[:3]): # Top 3
            arch = ctx.get('archetype', {})
            history_text += (
                f"Archetype {i+1}: {arch.get('name')} (Distance: {arch.get('distance'):.2f})\n"
                f"  - What happened: {arch.get('historical_summary')}\n"
                f"  - Typical Impact: {arch.get('typical_impact')}\n\n"
            )

        system_prompt = (
            "You are a Chief Risk Officer (CRO) at a top hedge fund. "
            "Your job is to synthesize conflicting signals into a concrete strategic assessment. "
            "You must balance the 'Situation Now' (News) with the 'Ghost of Risk Past' (History)."
        )

        prompt = (
            f"**ASSET**: {ticker}\n\n"
            f"**SIGNAL 1: THE SITUATION NOW (News)**\n"
            f"{scout_summary}\n\n"
            f"**SIGNAL 2: THE HISTORICAL PARALLELS (Archetypes)**\n"
            f"{history_text}\n\n"
            "**TASK**:\n"
            "Analyze if the current news actually aligns with these historical warning signs, or if the history is just noise.\n"
            "Produce a JSON object with the following fields:\n"
            "- 'verdict': One of ['Critical Risk', 'Elevated Risk', 'Neutral', 'Opportunity']\n"
            "- 'confidence': Integer 0-100\n"
            "- 'synthesis': A sharp, 1-paragraph executive summary connecting the dots.\n"
            "- 'action_plan': A list of 3 specific bullet points for the portfolio manager.\n"
            "\nOutput ONLY Valid JSON."
        )

        response = self._invoke_model(prompt, system_prompt)
        
        # Robust Parsing
        try:
            # Regex to find JSON block
            json_match = re.search(r'\{.*\}', response.replace("\n", " "), re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return data
            else:
                return json.loads(response) # Try direct parse
        except Exception as e:
            print(f"Advisor Parse Error: {e}")
            return {
                "verdict": "Unknown",
                "confidence": 0,
                "synthesis": f"Analysis failed to parse: {response[:100]}...",
                "action_plan": ["Check data feeds"]
            }
