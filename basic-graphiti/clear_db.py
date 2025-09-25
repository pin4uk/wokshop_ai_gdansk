import asyncio
import os
from dotenv import load_dotenv
from graphiti_core import Graphiti

# Load .env file from parent directory (root of the project)
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(env_path)

# Neo4j connection parameters from environment variables
# Make sure Neo4j Desktop is running with a local DBMS started
neo4j_uri = os.environ.get('NEO4J_URI')
neo4j_user = os.environ.get('NEO4J_USER') 
neo4j_password = os.environ.get('NEO4J_PASSWORD')

if not neo4j_uri or not neo4j_user or not neo4j_password:
    raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set in .env file')

async def clear_database():
    """Clear all data from the Neo4j database"""
    graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
    
    try:
        # Execute Cypher query to delete all nodes and relationships
        cypher_query = "MATCH (n) DETACH DELETE n"
        await graphiti.driver.execute_query(cypher_query)
        print("Database cleared successfully!")
        
    finally:
        await graphiti.close()

if __name__ == '__main__':
    asyncio.run(clear_database())