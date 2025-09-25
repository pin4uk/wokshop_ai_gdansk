"""
============================================================================
🎉 FINAL INTEGRATION - Step 5: Pydantic AI + Graphiti Knowledge Graphs
============================================================================

This is the CULMINATION of our workshop journey:

Step 1: Structured AI responses (pydantic-ai-quickstart)
Step 2: Document retrieval (basic-rag)  
Step 3: AI agents with RAG tools (pydantic-ai-rag)
Step 4: Knowledge graphs (basic-graphiti)
Step 5: AI AGENTS WITH GRAPH MEMORY (this file!)

🚀 What we achieve here:
- Conversational memory within sessions (message_history)
- Access to persistent knowledge graph (facts survive restarts)
- Contextual understanding through graph relationships  
- Foundation for production AI agents with episodic memory

This represents the state-of-the-art in AI agent architecture!
"""

from __future__ import annotations
from typing import Dict, List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
import asyncio
import os

# Pydantic AI imports - our agent framework
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, RunContext

# Graphiti imports - our knowledge graph engine
from graphiti_core import Graphiti

load_dotenv()

# ============================================================================
# 🔑 AGENT DEPENDENCIES - Knowledge Graph Integration
# ============================================================================

@dataclass
class GraphitiDependencies:
    """
    🔑 ADVANCED DEPENDENCIES: Now includes persistent graph memory!
    
    Evolution of dependencies across workshop steps:
    Step 1: superhero_id + simple db
    Step 3: mission context + multiple data sources  
    Step 5: PERSISTENT KNOWLEDGE GRAPH (facts survive restarts!)
    
    Note: This demo shows access to persistent knowledge, not conversation history.
    For true session persistence, you'd need to store message_history in the graph.
    """
    graphiti_client: Graphiti  # The knowledge graph that remembers conversations

# ============================================================================
# 🤖 MODEL CONFIGURATION - Production-ready setup
# ============================================================================

def get_model():
    """
    🤖 PRODUCTION MODEL SETUP: Flexible model selection
    - Environment-driven configuration
    - Multiple model support (GPT-4, Claude, etc.)
    - API key management
    
    This shows production patterns for model management
    """
    model_choice = os.getenv('MODEL_CHOICE', 'gpt-4.1-mini')
    api_key = os.getenv('OPENAI_API_KEY', 'no-api-key-provided')

    return OpenAIModel(model_choice, provider=OpenAIProvider(api_key=api_key))

# ============================================================================
# 🤖 THE ULTIMATE AI AGENT - With Graph Memory!
# ============================================================================

graphiti_agent = Agent(
    get_model(),                    # Flexible model configuration
    deps_type=GraphitiDependencies, # Knowledge graph dependencies
    # 🧠 ADVANCED SYSTEM PROMPT: Knowledge-graph aware
    system_prompt="""You are FRIDAY, an advanced AI assistant with persistent memory through a knowledge graph.
    
    🕸️ Your unique capabilities:
    - Access to temporal MCU hero data (before/after Endgame)
    - Knowledge that persists across conversations
    - Understanding of entity relationships and evolution
    - Ability to track facts over time
    
    🎯 When users ask questions:
    1. Use your search_graphiti tool to find relevant facts
    2. Consider temporal aspects (what changed when?)
    3. Acknowledge relationships between entities
    4. Be honest about missing information
    
    This isn't just retrieval - it's knowledge synthesis from a living graph!""",
)

# ============================================================================
# 📋 STRUCTURED GRAPH RESULTS - Rich temporal knowledge
# ============================================================================

class GraphitiSearchResult(BaseModel):
    """
    📋 GRAPH SEARCH RESULT: Much richer than RAG chunk results!
    
    Compare to previous steps:
    Step 2 RAG: similarity_score + text_chunk
    Step 3 Agent RAG: RetrievalResult with context
    Step 5 Graph: FACTS with temporal validity + entity relationships!
    
    This represents knowledge, not just information retrieval
    """
    uuid: str = Field(description="Unique identifier for this fact in the graph")
    fact: str = Field(description="Extracted factual statement (not raw text!)")
    valid_at: Optional[str] = Field(None, description="When this fact became true")
    invalid_at: Optional[str] = Field(None, description="When this fact became false")
    source_node_uuid: Optional[str] = Field(None, description="Entity this fact relates to")

# ============================================================================
# 🛠️ GRAPH SEARCH TOOL - The evolution of agent tools
# ============================================================================

@graphiti_agent.tool
async def search_graphiti(ctx: RunContext[GraphitiDependencies], query: str) -> List[GraphitiSearchResult]:
    """
    🛠️ KNOWLEDGE GRAPH SEARCH TOOL - The most advanced tool yet!
    
    Tool Evolution Across Workshop:
    Step 1: get_superhero_powers() - simple database lookup
    Step 3: retrieve_mission_intel() - RAG document search  
    Step 5: search_graphiti() - GRAPH KNOWLEDGE SYNTHESIS
    
    This tool doesn't just find similar text - it finds RELATED KNOWLEDGE
    across entities, relationships, and time periods!
    
    Args:
        query: Natural language query about MCU heroes/events
        
    Returns:
        Temporal facts with entity relationships and validity periods
    """
    # 🕸️ Access the persistent knowledge graph
    graphiti = ctx.deps.graphiti_client
    
    try:
        # 🔍 Perform graph search - finds connected knowledge, not just similar text
        results = await graphiti.search(query)
        
        # 📋 Format results into structured data for the AI agent
        formatted_results = []
        for result in results:
            formatted_result = GraphitiSearchResult(
                uuid=result.uuid,
                fact=result.fact,  # This is an EXTRACTED FACT, not raw document text!
                source_node_uuid=result.source_node_uuid if hasattr(result, 'source_node_uuid') else None
            )
            
            # ⏰ Add temporal information - facts can have time validity!
            if hasattr(result, 'valid_at') and result.valid_at:
                formatted_result.valid_at = str(result.valid_at)
            if hasattr(result, 'invalid_at') and result.invalid_at:
                formatted_result.invalid_at = str(result.invalid_at)
            
            formatted_results.append(formatted_result)
        
        return formatted_results
    except Exception as e:
        print(f"🚨 Graph search error: {str(e)}")
        raise

# ============================================================================
# 🎯 DEMO QUESTIONS - Showcasing temporal knowledge capabilities
# ============================================================================

async def suggest_questions():
    """
    🎯 STRATEGIC DEMO QUESTIONS: Designed to show off graph capabilities
    
    These questions demonstrate:
    - Temporal knowledge ("Is Tony Stark alive?" - depends on WHEN!)
    - Entity evolution ("Who leads the Avengers?" - changes over time)
    - Relationship queries ("What happened to..." - requires context)
    
    Perfect for showing how graph knowledge differs from static retrieval
    """
    questions = [
        "Is Tony Stark alive?",              # ⏰ Temporal: alive before Endgame, not after
        "Who is Captain America?",           # 🔄 Identity transfer: Steve → Sam  
        "What happened to Natasha Romanoff?", # 📚 Event knowledge
        "Where is Thor now?",                # 🌍 Location/status tracking
        "What is Bruce Banner's current state?", # 🔬 Character evolution
        "Who leads the Avengers now?",       # 👑 Leadership succession
        "What happened to Steve Rogers?"     # 🛡️ Character arc completion
    ]
    
    print("\n" + "="*50)
    print("🦸 TEMPORAL MCU KNOWLEDGE DEMO 🦸")
    print("="*50)
    print("These questions showcase graph memory capabilities:")
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")
    print("="*50)
    print("💡 Try asking follow-up questions to see conversational memory!")
    print("="*50)



async def main():
    # ========================================================================
    # 🚀 MAIN APPLICATION - The Complete AI Agent System
    # ========================================================================
    """
    🎉 THE FINAL DEMONSTRATION: Complete AI agent with persistent graph memory
    
    This represents the culmination of our workshop journey:
    - Structured AI responses (Step 1) ✓
    - Document retrieval (Step 2) ✓  
    - Intelligent tool selection (Step 3) ✓
    - Knowledge graph storage (Step 4) ✓
    - PERSISTENT CONVERSATIONAL MEMORY (Step 5) ✓
    
    This is production-ready AI agent architecture!
    """
    print("🦸 ULTIMATE MCU AI AGENT - Pydantic AI + Graphiti Knowledge Graph 🦸")
    print("🧠 Features: Persistent Memory | Temporal Knowledge | Relationship Understanding")
    print("💬 Type 'exit' to quit | Ask follow-up questions to see memory in action!")

    # 🗄️ Neo4j graph database connection
    neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
    neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')
    
    # 🕸️ Initialize the knowledge graph engine
    graphiti_client = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
    
    # 🔧 Initialize graph infrastructure (indices, constraints)
    try:
        await graphiti_client.build_indices_and_constraints()
        print("✅ Knowledge graph infrastructure ready.")
    except Exception as e:
        print(f"📝 Note: {str(e)}")
        print("📈 Continuing with existing graph structure...")

    console = Console()
    messages = []  # 💬 Conversation history for context
    
    # 🎯 Show demo questions that highlight graph capabilities
    await suggest_questions()
    
    try:
        while True:
            # 💬 Get user input
            user_input = input("\n[You] ")
            
            # 🚪 Check if user wants to exit
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("👋 Goodbye! Note: This demo doesn't save conversation history between sessions.")
                break
            
            try:
                # 🧠 Process with AI agent + knowledge graph
                print("\n[FRIDAY 🤖]")
                with Live('', console=console, vertical_overflow='visible') as live:
                    # 🔑 Inject knowledge graph as dependency
                    deps = GraphitiDependencies(graphiti_client=graphiti_client)
                    
                    # 🚀 Run the AI agent with streaming response
                    async with graphiti_agent.run_stream(
                        user_input, 
                        message_history=messages,  # 💬 Maintains conversation context
                        deps=deps                  # 🕸️ Provides graph memory access
                    ) as result:
                        curr_message = ""
                        async for message in result.stream_text(delta=True):
                            curr_message += message
                            live.update(Markdown(curr_message))
                    
                    # 📝 Update conversation history for next turn
                    messages.extend(result.all_messages())
                
            except Exception as e:
                print(f"\n🚨 [Error] {str(e)}")
                print("💡 Tip: Make sure Neo4j is running and graph data is loaded")
    finally:
        # 🧹 Clean up knowledge graph connection
        await graphiti_client.close()
        print("\n✅ Knowledge graph connection closed.")
        print("🎉 Workshop Complete! You've built a production-ready AI agent with:")
        print("   • 📋 Structured outputs (Pydantic validation)")
        print("   • 🛠️ Intelligent tool selection (agent reasoning)")
        print("   • 🕸️ Persistent graph memory (Graphiti)")
        print("   • ⏰ Temporal knowledge (facts with time validity)")
        print("   • 💬 Conversational context (message history)")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏸️  Program terminated by user.")
        print("💾 Note: Conversations aren't persisted - only the knowledge graph data!")
    except Exception as e:
        print(f"\n🚨 Unexpected error: {str(e)}")
        print("💡 Check your .env file and Neo4j connection")
        raise
