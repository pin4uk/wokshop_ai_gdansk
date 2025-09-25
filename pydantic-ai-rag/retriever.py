"""
============================================================================
🔍 RAG RETRIEVER - Same Tech as Step 2, Different Integration!
============================================================================

Key insight for workshop participants:
- SAME retrieval technology as basic-rag/
- But now it's used as an AGENT TOOL, not standalone pipeline
- This shows how RAG can be integrated into larger AI systems

Technical details (unchanged from Step 2):
- Manual cosine similarity in Python (no pgvector yet)
- Postgres stores embeddings as float arrays  
- Simple linear search through all chunks (no indexing)
"""
from __future__ import annotations

import asyncio
import math
import os
from typing import List, Tuple

from dotenv import load_dotenv
from openai import OpenAI

from db import get_conn

load_dotenv()

# Hard-coded model for pedagogical clarity (no env override complexity)
EMBED_MODEL = "text-embedding-3-small"

def embed_text(text: str) -> List[float]:
    """
    🧠 EMBEDDING GENERATION - Same as Step 2
    
    Workshop note: This function is IDENTICAL to basic-rag/retriever.py
    - Shows how you can reuse RAG components in AI agents
    - Same OpenAI embeddings, same quality
    - Different integration pattern (tool vs. pipeline)
    """
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY required for embeddings. Set in .env file.")
    
    client = OpenAI(api_key=key)
    response = client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    📐 SIMILARITY CALCULATION - Core RAG math (unchanged from Step 2)
    
    Workshop teaching point: Same similarity logic as basic-rag
    - Shows consistency across different integration patterns
    - Math doesn't change, architecture does
    
    Formula: cos(θ) = (a·b) / (|a| × |b|)
    Returns value between -1 and 1 (higher = more similar)
    """
    # Dot product: sum of element-wise multiplication
    dot_product = sum(x * y for x, y in zip(a, b))
    
    # Magnitude (L2 norm) of each vector
    magnitude_a = math.sqrt(sum(x * x for x in a)) or 1  # avoid division by zero
    magnitude_b = math.sqrt(sum(x * x for x in b)) or 1
    
    return dot_product / (magnitude_a * magnitude_b)

async def retrieve_async(query: str, k: int = 3) -> List[Tuple[float, str]]:
    """Retrieve top-k most similar chunks using manual cosine similarity.
    
    Workshop pipeline:
    1. Embed the query using OpenAI
    2. Load all chunks from Postgres (no vector indexing yet)
    3. Calculate cosine similarity for each chunk
    4. Sort by similarity and return top-k
    
    This shows the complete RAG retrieval process step-by-step.
    """
    # Step 1: Convert query to embedding vector
    query_embedding = embed_text(query)
    
    # Step 2: Load all stored chunks and their embeddings
    conn = await get_conn()
    rows = await conn.fetch("SELECT content, embedding FROM phase1_chunks")
    
    # Step 3: Calculate similarity scores for all chunks
    scored_chunks = []
    for row in rows:
        chunk_embedding = row['embedding']
        similarity_score = cosine_similarity(query_embedding, chunk_embedding)
        scored_chunks.append((similarity_score, row['content']))
    
    # Step 4: Sort by similarity (highest first) and return top-k
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return scored_chunks[:k]

def retrieve(query: str, k: int = 3) -> List[Tuple[float, str]]:
    """Synchronous wrapper for retrieve_async.
    
    Workshop convenience: Provides simple synchronous interface
    for the main RAG script while keeping async DB operations.
    """
    return asyncio.run(retrieve_async(query, k))

if __name__ == "__main__":
    # Simple test: retrieve chunks about OpenAI funding
    print("Testing Phase 1 retrieval...")
    try:
        results = retrieve("OpenAI funding")
        for similarity_score, text in results:
            print(f"Similarity: {similarity_score:.3f}")
            print(f"Text: {text[:80]}...")
            print("---")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you've run 'python phase1_simple_rag/ingest.py --reset' first")
