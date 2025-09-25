"""
MCU Heroes Evolution Script

This script demonstrates the evolution of MCU heroes over time using Graphiti.
It creates episodes about different MCU heroes before and after Endgame,
showing how their status and roles change over time.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.maintenance.graph_data_operations import clear_data

# Configure logging
logging.basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

load_dotenv()

# Neo4j connection parameters
neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')

if not neo4j_uri or not neo4j_user or not neo4j_password:
    raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')


async def add_episodes(graphiti, episodes, prefix="MCU Heroes", phase_time=None):
    """Add episodes to the graph with a given prefix and timestamp."""
    for i, episode in enumerate(episodes):
        await graphiti.add_episode(
            name=f'{prefix} {i}',
            episode_body=episode['content']
            if isinstance(episode['content'], str)
            else json.dumps(episode['content']),
            source=episode['type'],
            source_description=episode['description'],
            reference_time=phase_time or datetime.now(timezone.utc),
        )
        print(f'Added episode: {prefix} {i} ({episode["type"].value}) at {phase_time}')


async def get_user_choice():
    """Get user choice to continue or quit."""
    while True:
        choice = input("\nType 'continue' to proceed or 'quit' to exit: ").strip().lower()
        if choice in ['continue', 'quit']:
            return choice
        print("Invalid input. Please type 'continue' or 'quit'.")


async def phase1_initial_mcu_heroes(graphiti):
    """Phase 1: Add episodes about MCU heroes before Endgame."""
    print("\n=== PHASE 1: MCU HEROES INITIAL STATE ===")
    
    # Время ДО Endgame - апрель 25, 2019
    phase1_time = datetime(2019, 4, 25, tzinfo=timezone.utc)
    print(f"Setting timeline to: {phase1_time} (Pre-Endgame)")
    
    # Episodes about MCU heroes before Endgame
    episodes = [
        {
            'content': 'Tony Stark is alive and actively serving as Iron Man. He is a founding member of the Avengers and continues to develop advanced technology to protect the world.',
            'type': EpisodeType.text,
            'description': 'Hero status report',
        },
        {
            'content': 'Steve Rogers serves as Captain America and leads the Avengers. He is actively protecting the world and maintains his role as the moral compass of the team.',
            'type': EpisodeType.text,
            'description': 'Hero status report',
        },
        {
            'content': 'Thor is the King of Asgard and an active member of the Avengers. He wields Mjolnir and later Stormbreaker, and is one of the most powerful heroes in the team.',
            'type': EpisodeType.text,
            'description': 'Hero status report',
        },
        {
            'content': 'Natasha Romanoff, known as Black Widow, is alive and serves as a core member of the Avengers. She is an expert spy and assassin who fights alongside the team.',
            'type': EpisodeType.text,
            'description': 'Hero status report',
        },
        {
            'content': 'Bruce Banner and the Hulk are active members of the Avengers, though Banner struggles with controlling the Hulk transformation.',
            'type': EpisodeType.text,
            'description': 'Hero status report',
        },
        {
            'content': 'Clint Barton, known as Hawkeye, is an active Avenger with his family intact. He lives peacefully with his wife Laura and their children.',
            'type': EpisodeType.text,
            'description': 'Hero status report',
        },
        {
            'content': {
                'name': 'Tony Stark',
                'alias': 'Iron Man',
                'status': 'alive',
                'role': 'Active Avenger',
                'location': 'Earth',
                'powers': ['Genius intellect', 'Advanced technology', 'Iron Man suits'],
                'team_role': 'Founding member and tech specialist'
            },
            'type': EpisodeType.json,
            'description': 'Hero profile',
        },
        {
            'content': {
                'name': 'Steve Rogers',
                'alias': 'Captain America',
                'status': 'alive',
                'role': 'Active Avenger and team leader',
                'location': 'Earth',
                'powers': ['Super soldier serum', 'Enhanced strength', 'Vibranium shield'],
                'team_role': 'Leader and moral compass'
            },
            'type': EpisodeType.json,
            'description': 'Hero profile',
        },
        {
            'content': {
                'name': 'Thor Odinson',
                'alias': 'Thor',
                'status': 'alive',
                'role': 'King of Asgard and Avenger',
                'location': 'Asgard/Earth',
                'powers': ['God of Thunder', 'Mjolnir', 'Superhuman strength'],
                'team_role': 'Powerhouse and royal ally'
            },
            'type': EpisodeType.json,
            'description': 'Hero profile',
        },
        {
            'content': {
                'name': 'Natasha Romanoff',
                'alias': 'Black Widow',
                'status': 'alive',
                'role': 'Active Avenger',
                'location': 'Earth',
                'powers': ['Master spy', 'Expert combatant', 'Tactical genius'],
                'team_role': 'Intelligence and stealth operations'
            },
            'type': EpisodeType.json,
            'description': 'Hero profile',
        },
    ]
    
    await add_episodes(graphiti, episodes, "MCU Pre-Endgame", phase1_time)
    
    # Perform searches to show the results
    print("\nSearching for: 'Is Tony Stark alive?'")
    results = await graphiti.search('Is Tony Stark alive?')
    
    print('\nSearch Results:')
    for result in results:
        print(f'Fact: {result.fact}')
        print('---')
    
    print("\nSearching for: 'Who is Captain America?'")
    results = await graphiti.search('Who is Captain America?')
    
    print('\nSearch Results:')
    for result in results:
        print(f'Fact: {result.fact}')
        print('---')


async def phase2_endgame_aftermath(graphiti):
    """Phase 2: Updates after Endgame events."""
    print("\n=== PHASE 2: AFTER ENDGAME ===")
    
    # Время ПОСЛЕ Endgame - апрель 27, 2019
    phase2_time = datetime(2019, 4, 27, tzinfo=timezone.utc)
    print(f"Setting timeline to: {phase2_time} (Post-Endgame)")
    
    # Episodes about changes after Endgame
    episodes = [
        {
            'content': 'Tony Stark died heroically during the final battle with Thanos, sacrificing himself to save the universe by using the Infinity Stones. His death marked the end of an era for the Avengers.',
            'type': EpisodeType.text,
            'description': 'Hero status update',
        },
        {
            'content': 'Steve Rogers retired from his role as Captain America after returning the Infinity Stones. He lived a full life in the past and passed the Captain America mantle to Sam Wilson.',
            'type': EpisodeType.text,
            'description': 'Hero status update',
        },
        {
            'content': 'Sam Wilson has officially taken up the mantle of Captain America, inheriting the shield from Steve Rogers. He now leads the new generation of heroes.',
            'type': EpisodeType.text,
            'description': 'Hero status update',
        },
        {
            'content': 'Natasha Romanoff sacrificed herself on Vormir to obtain the Soul Stone, dying to help the Avengers defeat Thanos and restore half the universe.',
            'type': EpisodeType.text,
            'description': 'Hero status update',
        },
        {
            'content': 'Thor stepped down from his role as King of Asgard, passing leadership to Valkyrie. He now travels with the Guardians of the Galaxy seeking his own path.',
            'type': EpisodeType.text,
            'description': 'Hero status update',
        },
        {
            'content': 'Bruce Banner successfully integrated his personality with the Hulk, becoming "Smart Hulk" - retaining his intelligence while having permanent Hulk strength and appearance.',
            'type': EpisodeType.text,
            'description': 'Hero status update',
        },
        {
            'content': 'Clint Barton lost his family to the Snap but they were restored after the Blip. He temporarily became Ronin during the five-year period but has now returned to his family.',
            'type': EpisodeType.text,
            'description': 'Hero status update',
        },
        {
            'content': {
                'name': 'Tony Stark',
                'alias': 'Iron Man',
                'status': 'deceased',
                'role': 'Deceased hero - died saving universe',
                'location': 'N/A',
                'legacy': 'Sacrificed himself using Infinity Stones to defeat Thanos',
                'team_role': 'Former founding member - heroic sacrifice'
            },
            'type': EpisodeType.json,
            'description': 'Updated hero profile',
        },
        {
            'content': {
                'name': 'Steve Rogers',
                'alias': 'Former Captain America',
                'status': 'retired',
                'role': 'Retired - lived life in past',
                'location': 'Unknown/Past timeline',
                'current_captain_america': 'Sam Wilson',
                'team_role': 'Former leader - passed mantle to Sam Wilson'
            },
            'type': EpisodeType.json,
            'description': 'Updated hero profile',
        },
        {
            'content': {
                'name': 'Sam Wilson',
                'alias': 'Captain America',
                'status': 'alive',
                'role': 'Current Captain America',
                'location': 'Earth',
                'powers': ['Flight with wings', 'Vibranium shield', 'Military training'],
                'team_role': 'New leader of Avengers'
            },
            'type': EpisodeType.json,
            'description': 'New hero profile',
        },
        {
            'content': {
                'name': 'Natasha Romanoff',
                'alias': 'Black Widow',
                'status': 'deceased',
                'role': 'Deceased hero - died for Soul Stone',
                'location': 'N/A',
                'legacy': 'Sacrificed herself on Vormir to obtain Soul Stone',
                'team_role': 'Former core member - heroic sacrifice'
            },
            'type': EpisodeType.json,
            'description': 'Updated hero profile',
        },
    ]
    
    await add_episodes(graphiti, episodes, "MCU Post-Endgame", phase2_time)
    
    # Perform searches to show the results
    print("\nSearching for: 'Is Tony Stark alive?'")
    results = await graphiti.search('Is Tony Stark alive?')
    
    print('\nSearch Results:')
    for result in results:
        print(f'Fact: {result.fact}')
        print('---')
    
    print("\nSearching for: 'Who is Captain America now?'")
    results = await graphiti.search('Who is Captain America now?')
    
    print('\nSearch Results:')
    for result in results:
        print(f'Fact: {result.fact}')
        print('---')





async def run_phase1_only():
    """Run only Phase 1 with data clearing."""
    graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
    try:
        await graphiti.build_indices_and_constraints()
        print("Clearing existing graph data...")
        await clear_data(graphiti.driver)
        print("Graph data cleared successfully.")
        await phase1_initial_mcu_heroes(graphiti)
        print("\n=== PHASE 1 COMPLETE ===")
        print("Now run 'python ingest.py phase2' to add Phase 2 data")
    finally:
        await graphiti.close()
        print('\nConnection closed')

async def run_phase2_only():
    """Run only Phase 2 without clearing existing data."""
    graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
    try:
        await graphiti.build_indices_and_constraints()
        print("Adding Phase 2 data to existing graph...")
        await phase2_endgame_aftermath(graphiti)
        print("\n=== PHASE 2 COMPLETE ===")
        print("Now you can use agent.py to query the updated knowledge graph!")
    finally:
        await graphiti.close()
        print('\nConnection closed')

async def main():
    """Main function to run the MCU heroes evolution demonstration."""
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'phase1':
            await run_phase1_only()
            return
        elif sys.argv[1].lower() == 'phase2':
            await run_phase2_only()
            return
        else:
            print("Usage: python ingest.py [phase1|phase2]")
            print("  phase1 - Run Phase 1 only (clears existing data)")
            print("  phase2 - Run Phase 2 only (adds to existing data)")
            print("  (no args) - Run both phases interactively")
            return

    # Default behavior - interactive mode
    graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)

    try:
        await graphiti.build_indices_and_constraints()
        
        print("Clearing existing graph data...")
        await clear_data(graphiti.driver)
        print("Graph data cleared successfully.")
        
        # Phase 1: Initial MCU heroes state (before Endgame)
        await phase1_initial_mcu_heroes(graphiti)
        
        # Wait for user input
        choice = await get_user_choice()
        if choice == 'quit':
            return
        
        # Phase 2: After Endgame changes
        await phase2_endgame_aftermath(graphiti)
        
        print("\n=== MCU EVOLUTION COMPLETE ===")
        print("Now you can use agent.py to query the knowledge graph!")
        print("Try asking: 'Is Tony Stark alive?' or 'Who is Captain America?'")
        
    finally:
        await graphiti.close()
        print('\nConnection closed')


if __name__ == '__main__':
    asyncio.run(main())
