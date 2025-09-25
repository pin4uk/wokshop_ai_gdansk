"""
============================================================================
🕸️ GRAPHITI + NEO4J QUICKSTART - Step 4 of Workshop
============================================================================

This demonstrates KNOWLEDGE GRAPHS as the next evolution:

Step 1: Structured AI responses (simple data)
Step 2: RAG retrieval (documents → answers) 
Step 3: AI + RAG tools (intelligent document access)
Step 4: KNOWLEDGE GRAPHS (entities + relationships + time)

Key concepts:
🧠 Episodic Memory - AI remembers facts over time
🕸️ Graph Relationships - entities connected, not isolated
⏰ Temporal Knowledge - facts have validity periods
🔍 Graph-based Search - find related information through connections
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv

# Graphiti imports - the knowledge graph library
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

#################################################
# 🔧 CONFIGURATION - Neo4j Database Connection
#################################################
# Knowledge graphs need a GRAPH DATABASE (not SQL!)
# Neo4j stores entities as nodes, relationships as edges
# This is fundamentally different from RAG's vector storage
#################################################

# Configure logging to see what Graphiti is doing under the hood
logging.basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# Load environment variables (Neo4j connection details)
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(env_path)

# 🗄️ Neo4j connection - THE GRAPH DATABASE ENGINE
# Unlike RAG (Postgres with vectors), we need a GRAPH database
# Neo4j stores: Nodes (entities) + Relationships (connections) + Properties
neo4j_uri = os.environ.get('NEO4J_URI')          # e.g., bolt://localhost:7687
neo4j_user = os.environ.get('NEO4J_USER')        # e.g., neo4j
neo4j_password = os.environ.get('NEO4J_PASSWORD') # your Neo4j password

if not neo4j_uri or not neo4j_user or not neo4j_password:
    raise ValueError('🚨 NEO4J connection required! Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env')


# ============================================================================
# 📚 DATA LOADING - Episodes are the building blocks of knowledge graphs
# ============================================================================

def load_episodes_from_json():
    """
    📚 EPISODES = Units of Knowledge for Graph Building
    
    Key difference from RAG documents:
    - RAG: Static documents that get chunked and embedded
    - Graphiti: EPISODES that get processed into entities + relationships
    
    Episodes can be:
    - Text narratives (like "Tony Stark fought Thanos")
    - Structured JSON (like mission reports with metadata)
    
    Graphiti extracts: WHO did WHAT to WHOM, WHEN, WHERE
    """
    try:
        with open('episodes.json', 'r', encoding='utf-8') as f:
            episodes_data = json.load(f)
        
        # Convert type strings to EpisodeType enums
        episodes = []
        for episode in episodes_data:
            episode_copy = episode.copy()
            if episode_copy['type'] == 'text':
                episode_copy['type'] = EpisodeType.text      # Narrative text
            elif episode_copy['type'] == 'json':
                episode_copy['type'] = EpisodeType.json      # Structured data
            episodes.append(episode_copy)
        
        return episodes
    except FileNotFoundError:
        logger.error("episodes.json file not found")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing episodes.json: {e}")
        return []


async def main():
    #################################################
    # 🚀 INITIALIZATION - Setting up the Knowledge Graph
    #################################################
    # Unlike RAG (just connect to Postgres), knowledge graphs
    # need special setup: indices for fast graph traversal,
    # constraints for data integrity, etc.
    #################################################

    # 🕸️ Initialize Graphiti - The Knowledge Graph Engine
    graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)

    try:
        # 🔧 Build graph infrastructure (indices, constraints)
        # This is like "CREATE TABLE" in SQL, but for graph structures
        await graphiti.build_indices_and_constraints()

        #################################################
        # 📝 ADDING EPISODES - Building the Knowledge Graph
        #################################################
        # This is where the MAGIC happens:
        # Episodes → AI analysis → Entities + Relationships + Time
        # 
        # Compare to RAG ingestion:
        # RAG: Document → Chunks → Embeddings → Storage
        # Graphiti: Episode → Entity Extraction → Graph Building
        #################################################

        # 📚 Load episodes - our knowledge to be graphed
        episodes = load_episodes_from_json()
        
        if not episodes:
            logger.error("No episodes loaded. Please check episodes.json file.")
            return

        # 🧠 Add episodes to the graph - AI processes each one automatically
        print("🔄 Processing episodes into knowledge graph...")
        for i, episode in enumerate(episodes):
            await graphiti.add_episode(
                name=f'S.H.I.E.L.D. Archive Entry {i+1}',
                episode_body=episode['content']
                if isinstance(episode['content'], str)
                else json.dumps(episode['content']),
                source=episode['type'],
                source_description=episode['description'],
                reference_time=datetime.now(timezone.utc),  # ⏰ When this knowledge was recorded
            )
            print(f'✅ Added episode: S.H.I.E.L.D. Archive Entry {i+1} ({episode["type"].value})')
            # Behind the scenes: AI extracts entities, relationships, temporal info!

        #################################################
        # 🔍 BASIC SEARCH - Graph-powered knowledge retrieval
        #################################################
        # Key difference from RAG search:
        # RAG: Find similar document chunks
        # Graphiti: Find related FACTS and RELATIONSHIPS
        # 
        # Returns: Specific facts about entities and their connections
        #################################################

        print("\n🔍 Searching the knowledge graph...")
        print("Query: 'Who is Iron Man and what are his abilities?'")
        # 🕸️ Graph search: finds facts + relationships, not just similar text
        results = await graphiti.search('Who is Iron Man and what are his abilities?')

        # 📊 Display search results - Notice the structured facts!
        print('\n📊 KNOWLEDGE GRAPH SEARCH RESULTS:')
        for result in results:
            print(f'🆔 UUID: {result.uuid}')
            print(f'📝 FACT: {result.fact}')  # Specific, extracted knowledge
            if hasattr(result, 'valid_at') and result.valid_at:
                print(f'⏰ Valid from: {result.valid_at}')  # Temporal knowledge!
            if hasattr(result, 'invalid_at') and result.invalid_at:
                print(f'⏰ Valid until: {result.invalid_at}')  # Facts can expire!
            print('---')
        # Compare to RAG: RAG returns document chunks, Graphiti returns FACTS

        #################################################
        # 🎯 CENTER NODE SEARCH - Graph-based context ranking
        #################################################
        # This is UNIQUE to knowledge graphs!
        # RAG ranks by similarity to query
        # Graphiti can rank by GRAPH DISTANCE to a specific entity
        # 
        # Finds: "What's connected to Iron Man in the knowledge graph?"
        #################################################

        if results and len(results) > 0:
            # 🎯 Use a specific entity as the "center" of our search
            center_node_uuid = results[0].source_node_uuid

            print('\n🎯 GRAPH-DISTANCE RERANKING:')
            print(f'Center entity: {center_node_uuid}')
            print('Finding knowledge CONNECTED to this entity in the graph...')

            # 🕸️ Rerank results by graph proximity, not just text similarity
            reranked_results = await graphiti.search(
                'Who is Iron Man and what are his abilities?', center_node_uuid=center_node_uuid
            )

            # 📊 Display reranked results - notice the contextual ordering!
            print('\n📊 GRAPH-CONTEXT RERANKED RESULTS:')
            for result in reranked_results:
                print(f'🆔 UUID: {result.uuid}')
                print(f'📝 FACT: {result.fact}')
                if hasattr(result, 'valid_at') and result.valid_at:
                    print(f'⏰ Valid from: {result.valid_at}')
                if hasattr(result, 'invalid_at') and result.invalid_at:
                    print(f'⏰ Valid until: {result.invalid_at}')
                print('---')
            # These results are ordered by GRAPH RELATIONSHIPS, not just text similarity!
        else:
            print('❌ No results found in the initial search to use as center node.')

        #################################################
        # 🔧 NODE SEARCH - Advanced graph queries
        #################################################
        # Different types of graph searches:
        # 1. Edge search (relationships/facts) - what we did above
        # 2. NODE search (entities) - what we're doing now
        # 
        # This finds ENTITIES (people, objects, concepts) not just facts
        #################################################

        print('\n🔧 ADVANCED NODE SEARCH:')
        print('Finding ENTITIES (not just facts) related to: "Avengers and Enhanced Individuals"')

        # 🎛️ Use predefined search configuration and customize it
        node_search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        node_search_config.limit = 5  # Limit to 5 entities

        # 🕸️ Execute entity search - finds people, organizations, objects, etc.
        node_search_results = await graphiti._search(
            query='Avengers and Enhanced Individuals',
            config=node_search_config,
        )

        # 📊 Display discovered entities
        print('\n📊 DISCOVERED ENTITIES (NODES):')
        for node in node_search_results.nodes:
            print(f'🆔 Entity UUID: {node.uuid}')
            print(f'📛 Entity Name: {node.name}')
            node_summary = node.summary[:100] + '...' if len(node.summary) > 100 else node.summary
            print(f'📝 Summary: {node_summary}')
            print(f'🏷️  Labels: {", ".join(node.labels)}')  # What TYPE of entity (Person, Organization, etc.)
            print(f'⏰ Created: {node.created_at}')
            if hasattr(node, 'attributes') and node.attributes:
                print('🔧 Properties:')  # Additional entity metadata
                for key, value in node.attributes.items():
                    print(f'  • {key}: {value}')
            print('---')
        # These are ENTITIES extracted from episodes, with rich metadata!

    finally:
        #################################################
        # 🧹 CLEANUP - Proper resource management
        #################################################
        # Graph databases hold persistent connections
        # Always clean up to avoid connection leaks
        #################################################

        await graphiti.close()
        print('\n✅ Knowledge graph connection closed')
        print('🎉 Workshop Step 4 complete! You now understand:')
        print('   • 🕸️  Knowledge graphs vs document storage')  
        print('   • 🧠 Entity + relationship extraction')
        print('   • ⏰ Temporal knowledge (facts with time)')
        print('   • 🎯 Graph-distance ranking')
        print('   • 🔍 Multiple search patterns (facts vs entities)')


if __name__ == '__main__':
    asyncio.run(main())