import os
import boto3
import json
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
from dotenv import load_dotenv
from .archetypes import get_archetypes

load_dotenv()

class VectorEngine:
    def __init__(self, collection_name="risk_archetypes"):
        self.bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN")
        )
        # Initialize Persistent ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db_v3")
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        
        # Check if empty, if so, seed it
        if self.collection.count() == 0:
            self._seed_archetypes()

    def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using Bedrock Titan.
        """
        body = json.dumps({
            "inputText": text,
        })
        try:
            response = self.bedrock.invoke_model(
                modelId="amazon.titan-embed-text-v1",
                contentType="application/json",
                accept="application/json",
                body=body
            )
            response_body = json.loads(response.get("body").read())
            return response_body.get("embedding")
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 1536 # Titan V1 is 1536 dim

    def _seed_archetypes(self):
        """
        Embed and store the seed archetypes.
        """
        print("Seeding Vector DB with Archetypes...")
        archetypes = get_archetypes()
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        for arch in archetypes:
            ids.append(arch["id"])
            # We embed the rich summary
            text = f"{arch['name']}: {arch['summary']}"
            documents.append(text)
            
            # Store full data in metadata for retrieval
            meta = {k: str(v) for k, v in arch.items() if k != "summary"} # Store simple types
            meta["full_summary"] = arch["summary"] # Store summary in meta too
            metadatas.append(meta)
            
            emb = self._get_embedding(text)
            embeddings.append(emb)
            
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        print(f"Seeded {len(ids)} archetypes.")

    def find_matches(self, current_summary: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Finds the top k historical archetypes.
        """
        query_emb = self._get_embedding(current_summary)
        
        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=k
        )
        
        matches = []
        if not results['ids']:
            return matches
            
        # Parse result lists (list of lists)
        for i in range(len(results['ids'][0])):
            match_id = results['ids'][0][i]
            distance = results['distances'][0][i]
            metadata = results['metadatas'][0][i]
            
            matches.append({
                "archetype_id": match_id,
                "ticker": metadata.get("ticker"),
                "name": metadata.get("name"),
                "period": metadata.get("period"),
                "historical_summary": metadata.get("full_summary"),
                "typical_impact": metadata.get("typical_impact"),
                "distance": distance
            })
            
        return matches
