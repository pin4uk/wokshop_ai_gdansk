"""Pydantic AI Agent with Multiple Tools - Superhero Mission Intelligence System.

This demonstrates how to use Pydantic AI agents with multiple tools:
1. Document retrieval tool (RAG) - for mission intel and threat data
2. Superhero database tools - for team member capabilities and status
3. System prompt enhancement - for contextual superhero information

Key concepts:
- Multiple tools working together in one agent
- Context sharing through dependencies
- Rich superhero-themed use case for mission planning
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

from retriever import retrieve_async

load_dotenv()

# Hard-coded model for pedagogical clarity
CHAT_MODEL = "gpt-4o-mini"

# Mock Superhero Database - MCU Heroes with Mission-Relevant Data
@dataclass
class Superhero:
    id: int
    name: str
    powers: Dict[str, int]  # Power levels 0-100
    status: str  # "active", "injured", "unavailable", "on_mission"
    location: str
    specialties: List[str]

SUPERHERO_DB = {
    1: Superhero(
        id=1, 
        name="Iron Man", 
        powers={"intelligence": 100, "technology": 95, "flight": 90, "energy_projection": 85},
        status="active",
        location="New York", 
        specialties=["technology", "aerial_combat", "strategy"]
    ),
    2: Superhero(
        id=2,
        name="Captain America", 
        powers={"strength": 90, "leadership": 100, "shield_mastery": 95, "tactical_analysis": 88},
        status="active",
        location="Washington DC",
        specialties=["leadership", "ground_combat", "infiltration"] 
    ),
    3: Superhero(
        id=3,
        name="Thor",
        powers={"strength": 98, "lightning": 100, "flight": 85, "durability": 95},
        status="on_mission",
        location="Asgard",
        specialties=["heavy_combat", "weather_control", "divine_magic"]
    ),
    4: Superhero(
        id=4,
        name="Black Widow",
        powers={"agility": 88, "stealth": 95, "combat_skills": 90, "intelligence": 85}, 
        status="active",
        location="Europe",
        specialties=["espionage", "infiltration", "assassination", "stealth"]
    ),
    5: Superhero(
        id=5,
        name="Hulk",
        powers={"strength": 100, "durability": 98, "rage_power": 100, "healing": 85},
        status="injured", 
        location="Somewhere in hiding",
        specialties=["heavy_combat", "destruction", "intimidation", "containment"]
    )
}

class SuperheroDatabase:
    """Mock database connection for superhero operations."""
    
    async def get_hero_by_id(self, hero_id: int) -> Superhero | None:
        return SUPERHERO_DB.get(hero_id)
    
    async def get_available_heroes(self) -> List[Superhero]:
        return [hero for hero in SUPERHERO_DB.values() if hero.status == "active"]
    
    async def get_heroes_by_specialty(self, specialty: str) -> List[Superhero]:
        return [hero for hero in SUPERHERO_DB.values() 
                if specialty.lower() in [s.lower() for s in hero.specialties]]

@dataclass 
class MissionIntelDependencies:
    """Dependencies for the Superhero Mission Intelligence agent.
    
    Includes both database access and mission context.
    """
    mission_id: str = "MISSION_001"
    clearance_level: int = 5  # 1-10, affects what intel can be accessed
    superhero_db: SuperheroDatabase = None
    
    def __post_init__(self):
        if self.superhero_db is None:
            self.superhero_db = SuperheroDatabase()


class RetrievalResult(BaseModel):
    """Structured result from retrieval tool."""
    similarity_score: float = Field(description="Cosine similarity score")
    content: str = Field(description="Retrieved text content")

class SuperheroInfo(BaseModel):
    """Structured superhero information."""
    name: str = Field(description="Superhero name")
    powers: Dict[str, int] = Field(description="Power levels (0-100)")
    status: str = Field(description="Current operational status")
    location: str = Field(description="Current location")
    specialties: List[str] = Field(description="Areas of expertise")

# Create the agent
mission_intel_agent = Agent(
    f"openai:{CHAT_MODEL}",
    deps_type=MissionIntelDependencies,
    system_prompt=(
        "You are FRIDAY, the advanced AI assistant for the Avengers. "
        "You help with mission planning by analyzing intelligence reports and superhero capabilities. "
        "Use your tools to:\n"
        "1. Retrieve mission intel and threat data from classified documents\n" 
        "2. Look up superhero team member capabilities and availability\n"
        "3. Provide strategic recommendations for team composition and tactics\n\n"
        "Always be tactical, professional, and consider both the mission requirements and hero safety."
    ),
)


@mission_intel_agent.system_prompt
async def add_mission_context(ctx: RunContext[MissionIntelDependencies]) -> str:
    """Add mission context to the system prompt."""
    return f"Current mission: {ctx.deps.mission_id} | Clearance Level: {ctx.deps.clearance_level}/10"

@mission_intel_agent.tool
async def retrieve_mission_intel(
    ctx: RunContext[MissionIntelDependencies],
    query: str,
    k: int = 3
) -> List[RetrievalResult]:
    """Retrieve classified mission intelligence and threat data from secure documents.
    
    Args:
        query: Intelligence query (e.g. "Hydra bases", "alien technology", "villain capabilities") 
        k: Number of top classified reports to return (1-5)
        
    Returns:
        List of intelligence chunks with security ratings and content
    """
    # Use the existing retriever from basic-rag
    raw_results = await retrieve_async(query, k)
    
    # Convert to structured results with mission context
    results = []
    for similarity_score, content in raw_results:
        results.append(RetrievalResult(
            similarity_score=similarity_score,
            content=f"[CLEARANCE {ctx.deps.clearance_level}] {content}"
        ))
    
    return results

@mission_intel_agent.tool  
async def get_available_heroes(
    ctx: RunContext[MissionIntelDependencies]
) -> List[SuperheroInfo]:
    """Get list of all currently available superheroes for mission deployment.
    
    Returns:
        List of active heroes with their current capabilities and status
    """
    available_heroes = await ctx.deps.superhero_db.get_available_heroes()
    
    return [SuperheroInfo(
        name=hero.name,
        powers=hero.powers,
        status=hero.status, 
        location=hero.location,
        specialties=hero.specialties
    ) for hero in available_heroes]

@mission_intel_agent.tool
async def get_heroes_by_specialty(
    ctx: RunContext[MissionIntelDependencies],
    specialty: str
) -> List[SuperheroInfo]:
    """Find heroes with specific combat specialties or capabilities.
    
    Shows ALL heroes with the specialty, regardless of availability status.
    Use this when intel mentions specific requirements like "divine powers", "mystical abilities", 
    "supernatural", "technology", "heavy combat", etc.
    
    Args:
        specialty: Required specialty (e.g. "divine_magic", "technology", "stealth", "heavy_combat", "leadership")
        
    Returns:
        List of ALL heroes who specialize in the requested area (available and unavailable)
    """
    specialist_heroes = await ctx.deps.superhero_db.get_heroes_by_specialty(specialty)
    
    return [SuperheroInfo(
        name=hero.name,
        powers=hero.powers,
        status=hero.status,
        location=hero.location, 
        specialties=hero.specialties
    ) for hero in specialist_heroes]



async def plan_mission(question: str, mission_id: str = "AVENGERS_001") -> str:
    """Run the mission intelligence agent to analyze threats and recommend team composition.
    
    Args:
        question: Mission briefing or tactical question
        mission_id: Mission identifier
        
    Returns:
        FRIDAY's tactical analysis and recommendations
    """
    deps = MissionIntelDependencies(mission_id=mission_id, clearance_level=8)
    result = await mission_intel_agent.run(question, deps=deps)
    return result.output


async def main() -> None:
    """Demonstrate the FRIDAY Mission Intelligence System with multiple tools."""
    
    print("🚀 FRIDAY - AVENGERS MISSION INTELLIGENCE SYSTEM")
    print("=" * 80)
    print("🤖 Multi-Tool Pydantic AI Agent: Document Retrieval + Superhero Database")
    print("=" * 80)
    print()
    
    # Mission scenarios that showcase RAG retrieving relevant intel + hero matching
    scenarios = [
        {
            "mission": "OPERATION_THUNDERSTRIKE", 
            "briefing": "Hydra facility with alien technology needs infiltration. What specific threats should we expect and which heroes can handle energy shields and tech security?"
        },
        {
            "mission": "OPERATION_CITYDEFENSE",
            "briefing": "Urban invasion with flying enemies attacking downtown. What's the threat assessment and who can provide aerial superiority and ground defense?"
        },
        {
            "mission": "OPERATION_GHOSTHUNTER", 
            "briefing": "Supernatural entities and dark magic rifts appearing in Scotland. What mystical threats are we facing and which heroes have divine powers?"
        },
        {
            "mission": "OPERATION_SHADOWNETWORK",
            "briefing": "International spy network targeting superhero identities. What are their capabilities and who's best for covert intelligence operations?"
        },
        {
            "mission": "OPERATION_REDEMPTION",
            "briefing": "Rogue enhanced individual with superhuman strength on rampage. What psychological factors are involved and who can safely contain them?"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"📋 MISSION {i}: {scenario['mission']}")
        print("=" * 60)
        print(f"🎯 BRIEFING: {scenario['briefing']}")
        print("-" * 60)
        
        try:
            tactical_analysis = await plan_mission(scenario['briefing'], scenario['mission'])
            print(f"🤖 FRIDAY ANALYSIS:")
            print(f"{tactical_analysis}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()
        print("=" * 80)
        print()


if __name__ == "__main__":
    asyncio.run(main())