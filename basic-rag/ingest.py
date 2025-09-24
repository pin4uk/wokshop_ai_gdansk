"""Phase 1 ingestion: Basic RAG pipeline with Postgres storage.

This phase demonstrates the fundamental ingestion steps:
1. Load documents from files
2. Split into chunks (simple word-based chunking)
3. Generate embeddings (OpenAI API)
4. Store in Postgres as float arrays

Creates phase1_documents and phase1_chunks tables.
"""
from __future__ import annotations

import asyncio
import glob
import os
from typing import List

from db import get_conn, init_schema, reset_schema

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Hard-coded model for pedagogical clarity
EMBED_MODEL = "text-embedding-3-small"

# Simple chunking parameters for demo
CHUNK_SIZE = 120  # words per chunk
OVERLAP = 20      # words of overlap between chunks
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def embed_text(text: str) -> List[float]:
    """Generate embeddings using OpenAI API.
    
    Workshop note: Each chunk gets converted to a vector representation.
    This is the same function used in retrieval for query embedding.
    """
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY required. Set in .env file.")
    
    client = OpenAI(api_key=key)
    response = client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding

def chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks.
    
    Workshop chunking strategy:
    - Simple word-based splitting (no sentence awareness)
    - Fixed overlap to preserve context across boundaries
    - Small chunks for demo purposes (real apps often use 200-500 words)
    """
    words = text.split()
    chunks = []
    i = 0
    
    while i < len(words):
        # Take CHUNK_SIZE words starting at position i
        chunk_words = words[i:i + CHUNK_SIZE]
        if not chunk_words:
            break
        
        chunks.append(" ".join(chunk_words))
        
        # Move forward by (CHUNK_SIZE - OVERLAP) to create overlap
        i += CHUNK_SIZE - OVERLAP
    
    return chunks

async def ingest_documents(reset: bool = False) -> None:
    """Complete ingestion pipeline for Phase 1.
    
    Pipeline steps:
    1. Initialize database schema (create tables)
    2. Load documents from data/ directory
    3. Split documents into chunks
    4. Generate embeddings for each chunk
    5. Store in Postgres with float[] arrays
    """
    # Step 1: Setup database
    if reset:
        print("🗑️  Resetting Phase 1 schema...")
        await reset_schema()
    else:
        await init_schema()
    
    conn = await get_conn()
    
    # Step 2: Load documents from data directory
    md_files = glob.glob(os.path.join(DATA_DIR, "*.md"))
    if not md_files:
        print(f"❌ No .md files found in {DATA_DIR}")
        return
    
    print(f"📁 Found {len(md_files)} documents to process")
    
    total_chunks = 0
    for filepath in md_files:
        filename = os.path.basename(filepath)
        print(f"📄 Processing {filename}...")
        
        # Step 3: Read and chunk document
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print(f"⚠️  Skipping empty file: {filename}")
            continue
        
        # Insert document record and get the ID
        doc_id = await conn.fetchval(
            "INSERT INTO phase1_documents (title, content) VALUES ($1, $2) ON CONFLICT (title) DO UPDATE SET content = EXCLUDED.content RETURNING id",
            filename, content
        )
        
        # Step 4: Create chunks and embeddings
        chunks = chunk_text(content)
        print(f"  📝 Created {len(chunks)} chunks")
        
        for i, chunk_text_content in enumerate(chunks):
            print(f"  🔮 Embedding chunk {i+1}/{len(chunks)}...", end=" ")
            
            try:
                # Generate embedding for this chunk
                embedding = embed_text(chunk_text_content)
                
                # Step 5: Store chunk with embedding
                await conn.execute(
                    "INSERT INTO phase1_chunks (document_id, chunk_index, content, embedding) VALUES ($1, $2, $3, $4) ON CONFLICT (document_id, chunk_index) DO NOTHING",
                    doc_id, i, chunk_text_content, embedding
                )
                print("✅")
                total_chunks += 1
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print(f"\n🎉 Ingestion complete! Processed {total_chunks} chunks total.")
    print("Ready for retrieval. Try:")
    print("  python phase1_simple_rag/rag.py 'What companies received funding?'")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 1 RAG Ingestion")
    parser.add_argument(
        '--reset', action='store_true', 
        help='Drop and recreate Phase 1 tables before ingestion'
    )
    args = parser.parse_args()
    
    print("🚀 Phase 1 Simple RAG - Document Ingestion")
    print("=" * 50)
    asyncio.run(ingest_documents(reset=args.reset))

