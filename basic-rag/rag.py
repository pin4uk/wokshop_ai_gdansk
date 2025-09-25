"""End-to-end simple RAG script for Phase 1 (Postgres-backed).

This phase demonstrates the complete RAG pipeline:
1. Question → Embedding (OpenAI API)
2. Similarity Search → Top-k chunks (manual cosine in Python)  
3. Context Assembly → Prompt template
4. Generation → LLM response (OpenAI chat completion)

Usage:
    python rag.py  (interactive mode with predefined questions)
    python rag.py "Your question"  (command-line mode)

Environment:
    OPENAI_API_KEY   (required for real embeddings/chat)
    DATABASE_URL     (required for retrieval from Postgres)
"""
from __future__ import annotations

import asyncio
import os
import sys
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from retriever import retrieve

load_dotenv()

# Hard-coded model for pedagogical clarity
CHAT_MODEL = "gpt-4o-mini"

def chat_completion(messages: List[Dict[str, Any]]) -> str:
    """Generate LLM response using OpenAI chat completion.
    
    Workshop teaching point: This is the 'Generation' step of RAG.
    The retrieved context is already embedded in the prompt.
    """
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY required for Phase 1. Set in .env file.")
    
    client = OpenAI(api_key=key)
    
    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL, 
            messages=messages
        )
        return response.choices[0].message.content or "No response generated"
    except Exception as e:
        # Graceful degradation for network/quota issues
        return f"API ERROR ({e.__class__.__name__}): Unable to generate response"

# RAG prompt template - combines retrieved context with user question
RAG_TEMPLATE = (
    "You are a knowledgeable consultant specializing in superheroes from the Marvel Cinematic Universe (MCU, not comics).\n"
    "Answer the user's question based PRIMARILY on the provided context below.\n"
    "The context contains the most up-to-date and accurate information available.\n"
    "Do not speculate about future events or discuss content from unreleased films or series.\n"
    "If the context provides information that differs from your training data, prioritize the context.\n"
    "If the context doesn't contain enough information to fully answer the question, you may supplement\n"
    "with your general knowledge, but clearly indicate what comes from the context vs. general knowledge.\n"
    "\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer:"
)

def print_rag_result(question: str, top_chunks: List[tuple], response: str) -> None:
    """Pretty print the RAG result similar to superhero analysis."""
    print("=" * 80)
    print("🤖 RAG SYSTEM ANALYSIS")
    print("=" * 80)
    print(f"❓ Question: {question}")
    print("-" * 80)
    
    print("📚 RETRIEVED CONTEXT:")
    if top_chunks:
        for i, (similarity, text) in enumerate(top_chunks, 1):
            print(f"   [{i}] Similarity: {similarity:.3f}")
            # Split long text into multiple lines for better readability
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= 70:
                    current_line += (" " if current_line else "") + word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            for line in lines:
                print(f"       {line}")
            print()
    else:
        print("   ❌ No relevant context found")
    
    print("-" * 80)
    print("🎯 GENERATED ANSWER:")
    # Split response into readable lines
    response_words = response.split()
    response_lines = []
    current_line = ""
    
    for word in response_words:
        if len(current_line + " " + word) <= 75:
            current_line += (" " if current_line else "") + word
        else:
            if current_line:
                response_lines.append(current_line)
            current_line = word
    if current_line:
        response_lines.append(current_line)
    
    for line in response_lines:
        print(f"   {line}")
    
    print("=" * 80)
    print()

def answer_question(question: str) -> None:
    """Complete RAG pipeline: Retrieve → Augment → Generate.
    
    Workshop pipeline demonstration:
    1. Retrieve: Get similar chunks from vector search
    2. Augment: Build prompt with retrieved context  
    3. Generate: Get LLM response using augmented prompt
    """
    print(f"🔍 Processing: {question}")
    try:
        # Retrieve top-k most similar chunks
        top_chunks = retrieve(question, k=3)
        
        # Format context with similarity scores for transparency
        context_lines = []
        for similarity, text in top_chunks:
            context_lines.append(f"[Similarity: {similarity:.3f}] {text}")
        context = "\n".join(context_lines)
        
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        context = f"(No context available: {e})"
        top_chunks = []
    
    # Build RAG prompt
    prompt = RAG_TEMPLATE.format(context=context, question=question)
    
    # Generate response
    response = chat_completion([{"role": "user", "content": prompt}])
    
    # Pretty print the results
    print_rag_result(question, top_chunks, response)

def main() -> None:
    """Interactive main function with one demo question."""
    print("🌟 BASIC RAG SYSTEM DEMO 🌟")
    print()
    
    # Check if question provided via command line
    if len(sys.argv) >= 2:
        question = sys.argv[1]
        answer_question(question)
        return
    
    # Single demo question
    demo_question = "Have Wolverine and Deadpool ever met?"
    
    print("🎯 Running demo question:")
    answer_question(demo_question)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        # Command-line mode (original behavior)
        question = sys.argv[1]
        print(f"🚀 RAG Query: {question}")
        print()
        answer_question(question)
    else:
        # Interactive mode with demo questions
        main()
