"""
============================================================================
🦸‍♂️ PYDANTIC AI + RAG INTEGRATION - Step 3 of Workshop
============================================================================

This demonstrates the EVOLUTION from basic RAG to intelligent AI agents:
1. 🧠 Pydantic AI Agent with multiple tools
2. 📚 RAG as an agent tool (not standalone pipeline)
3. 🗄️ Multiple data sources working together
4. 📋 Structured outputs from unstructured documents

Key learning points:
- RAG becomes a TOOL that AI can choose to use
- Multiple tools working together in one agent
- Context sharing through dependencies
- From "dumb" retrieval to "smart" agent decisions
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

from retriever import retrieve_async

# Load environment variables (API keys, database URLs)
load_dotenv()

# Hard-coded model for workshop clarity
CHAT_MODEL = "gpt-4o-mini"

# ============================================================================
# 🗄️ MOCK DATABASE - Enhanced superhero data for complex missions
# ============================================================================
# Notice how this is richer than the quickstart - more fields, more context
@dataclass
class Superhero:
    """Enhanced superhero data model for mission planning"""
    id: int
    name: str
    powers: Dict[str, int]  # Power levels 0-100 (more detailed than quickstart)
    status: str  # "active", "injured", "unavailable", "on_mission" 
    location: str           # Geographic availability
    specialties: List[str]  # Mission-relevant skills

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
    """
    🗄️ DATABASE ACCESS LAYER - More sophisticated than quickstart
    - Multiple query methods (by ID, availability, specialty)
    - Real-world mission planning scenarios
    - Async methods for database operations
    """
    
    async def get_hero_by_id(self, hero_id: int) -> Superhero | None:
        """Fetch specific hero by ID"""
        return SUPERHERO_DB.get(hero_id)
    
    async def get_available_heroes(self) -> List[Superhero]:
        """Get only heroes currently available for missions"""
        return [hero for hero in SUPERHERO_DB.values() if hero.status == "active"]
    
    async def get_heroes_by_specialty(self, specialty: str) -> List[Superhero]:
        """Find heroes with specific combat/mission specialties"""
        return [hero for hero in SUPERHERO_DB.values() 
                if specialty.lower() in [s.lower() for s in hero.specialties]]

# ============================================================================
# 🔑 AGENT DEPENDENCIES - More Complex Than Quickstart
# ============================================================================

@dataclass 
class MissionIntelDependencies:
    """
    🔑 ENHANCED DEPENDENCIES: Multiple data sources for the agent
    - Mission context (ID, clearance level)
    - Database connections 
    - Security/access control
    
    Compare to quickstart: just superhero_id + db connection
    Here: mission planning requires MORE context!
    """
    mission_id: str = "MISSION_001"
    clearance_level: int = 5  # 1-10, affects what intel can be accessed
    superhero_db: SuperheroDatabase = None
    
    def __post_init__(self):
        if self.superhero_db is None:
            self.superhero_db = SuperheroDatabase()


# ============================================================================
# 📋 STRUCTURED DATA MODELS - Multiple output types for different tools
# ============================================================================

class RetrievalResult(BaseModel):
    """
    📋 RAG TOOL OUTPUT: Structured results from document retrieval
    - Not just raw text - includes similarity scores!
    - Security clearance levels
    - Pydantic validation ensures clean data
    """
    similarity_score: float = Field(description="Cosine similarity score")
    content: str = Field(description="Retrieved text content")

class SuperheroInfo(BaseModel):
    """
    📋 HERO TOOL OUTPUT: Structured superhero information
    - More detailed than quickstart's simple data
    - Mission-relevant fields (status, location, specialties)
    - Type-safe access to complex hero data
    """
    name: str = Field(description="Superhero name")
    powers: Dict[str, int] = Field(description="Power levels (0-100)")
    status: str = Field(description="Current operational status")
    location: str = Field(description="Current location")
    specialties: List[str] = Field(description="Areas of expertise")

# ============================================================================
# 🤖 THE AI AGENT - Now with MULTIPLE TOOLS!
# ============================================================================

mission_intel_agent = Agent(
    f"openai:{CHAT_MODEL}",
    deps_type=MissionIntelDependencies,    # More complex dependencies
    # NO output_type here - let the agent return natural language responses
    # (Each TOOL has structured output, but the agent's final response is flexible)
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


# ============================================================================
# 🧠 DYNAMIC SYSTEM PROMPT - Mission-aware context
# ============================================================================

@mission_intel_agent.system_prompt
async def add_mission_context(ctx: RunContext[MissionIntelDependencies]) -> str:
    """
    🧠 DYNAMIC CONTEXT: Add mission-specific information to prompt
    - Mission ID and clearance level change per conversation
    - Makes the agent aware of security constraints
    - Compare to quickstart: just superhero name vs. mission context
    """
    return f"Current mission: {ctx.deps.mission_id} | Clearance Level: {ctx.deps.clearance_level}/10"

# ============================================================================
# 🛠️ AGENT TOOLS - Multiple tools working together
# ============================================================================

@mission_intel_agent.tool
async def retrieve_mission_intel(
    ctx: RunContext[MissionIntelDependencies],
    query: str,
    k: int = 3
) -> List[RetrievalResult]:
    """
    🛠️ RAG TOOL: This is where RAG becomes an AGENT TOOL!
    
    Key difference from basic-rag:
    - RAG is no longer the main pipeline
    - It's a tool the agent can CHOOSE to use
    - Returns structured data (RetrievalResult), not raw text
    - Agent decides WHEN to retrieve documents based on the conversation
    
    Args:
        query: Intelligence query (e.g. "Hydra bases", "alien technology") 
        k: Number of top classified reports to return (1-5)
        
    Returns:
        Structured intelligence with security clearance context
    """
    # Use the existing retriever from basic-rag (same tech, different integration!)
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
    """
    🛠️ HERO DATABASE TOOL: Access live superhero availability
    
    Demonstrates:
    - Multiple data sources (documents + database)
    - Real-time data access through dependencies
    - Structured output for complex queries
    
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
    """
    🛠️ SPECIALIST SEARCH TOOL: Find heroes with specific capabilities
    
    Key insight: The AI agent can now REASON about which tool to use:
    - Need general availability? Use get_available_heroes()
    - Need specific skills? Use this tool
    - Need threat intel? Use retrieve_mission_intel()
    
    The agent chooses the RIGHT tool for the situation!
    
    Args:
        specialty: Required specialty (e.g. "divine_magic", "technology", "stealth")
        
    Returns:
        List of ALL heroes who specialize in the requested area
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
    # ========================================================================
    # 🚀 DEMONSTRATION - Evolution from basic RAG to intelligent agent
    # ========================================================================
    """
    Shows the key difference between Step 2 (basic RAG) and Step 3 (Pydantic + RAG):
    
    Step 2: Human asks question → RAG retrieves → LLM generates answer
    Step 3: Human asks question → AI AGENT decides which tools to use → Structured response
    
    The agent can now:
    - Choose when to retrieve documents vs. query database
    - Combine multiple data sources intelligently  
    - Return structured, actionable intelligence
    """
    
    print("🚀 FRIDAY - AVENGERS MISSION INTELLIGENCE SYSTEM")
    print("=" * 80)
    print("� EVOLUTION: From Basic RAG → Intelligent Multi-Tool Agent")
    print("📊 RAG + Database + Structured Reasoning")
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