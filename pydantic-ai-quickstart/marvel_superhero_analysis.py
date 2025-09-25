from dataclasses import dataclass
from typing import Any
import asyncio

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from dotenv import load_dotenv


# Load environment variables from .env file (API keys, etc.)
load_dotenv()


# ============================================================================
# MOCK DATABASE SECTION - Simulates external data sources
# ============================================================================
# This represents the data that our AI agent will need to access

@dataclass
class Superhero:
    """Data model for superhero information"""
    id: int
    name: str
    powers: dict[str, Any]  # Power ratings from 0-100

# Mock superhero database - in real app this would be a proper database
SUPERHERO_DB = {
    42: Superhero(id=42, name="Spider-Man", powers={"strength": 85, "agility": 95, "web_slinging": 100}),
    43: Superhero(id=43, name="Iron Man", powers={"intelligence": 100, "technology": 95, "flight": 90}),
    44: Superhero(id=44, name="Captain America", powers={"strength": 90, "leadership": 100, "shield_mastery": 95}),
}

class DatabaseConn:
    """
    Database connection class - simulates async database operations
    In production, this would connect to PostgreSQL, MongoDB, etc.
    """
    
    async def superhero_name(self, id: int) -> str:
        """Fetch superhero name by ID"""
        superhero = SUPERHERO_DB.get(id)
        return superhero.name if superhero else "Unknown Superhero"

    async def latest_powers(self, id: int) -> dict[str, Any]:
        """Fetch current power levels for a superhero"""
        superhero = SUPERHERO_DB.get(id)
        return superhero.powers if superhero else {"strength": 0, "agility": 0, "special_ability": "None"}


# ============================================================================
# PYDANTIC AI CORE COMPONENTS
# ============================================================================

@dataclass
class SuperheroAnalysisDependencies:
    """
    🔑 DEPENDENCIES: External resources the AI agent needs
    - Gets injected into the agent's context
    - Allows agent to access databases, APIs, etc.
    """
    superhero_id: int  # Which superhero we're analyzing
    db: DatabaseConn   # Database connection


class SuperheroAnalysisOutput(BaseModel):
    """
    📋 STRUCTURED OUTPUT: Defines exactly what the AI must return
    - Pydantic model ensures type safety and validation
    - AI cannot return malformed data - it's validated automatically!
    """
    response_text: str = Field(description="Analysis of the superhero's situation")
    recommend_backup: bool = Field(description="Should recommend calling for backup")
    threat_level: int = Field(description="Threat level from 0 to 10", ge=0, le=10)  # ge/le = validation constraints


# ============================================================================
# 🤖 THE AI AGENT - The heart of Pydantic AI
# ============================================================================

superhero_agent = Agent(
    "openai:gpt-4o",                                    # Model to use
    deps_type=SuperheroAnalysisDependencies,           # What dependencies it needs
    output_type=SuperheroAnalysisOutput,               # What it must return (structured!)
    system_prompt=(                                     # Basic instructions
        "You are a superhero mission analyst for the Avengers. "
        "Analyze superhero situations and provide strategic recommendations."
    ),
)


# ============================================================================
# 🧠 DYNAMIC SYSTEM PROMPT - Adds context-specific information
# ============================================================================

@superhero_agent.system_prompt
async def add_superhero_name(ctx: RunContext[SuperheroAnalysisDependencies]) -> str:
    """
    🔄 DYNAMIC PROMPT: This function runs before each conversation
    - Fetches fresh data from database
    - Adds it to the AI's system prompt
    - Makes the prompt context-aware!
    """
    superhero_name = await ctx.deps.db.superhero_name(id=ctx.deps.superhero_id)
    return f"The superhero's name is {superhero_name!r}."


# ============================================================================
# 🛠️ AGENT TOOLS - Functions the AI can call to get real-time data
# ============================================================================

@superhero_agent.tool
async def latest_powers(ctx: RunContext[SuperheroAnalysisDependencies]) -> dict[str, Any]:
    """
    🔧 AI TOOL: The agent can call this function when it needs current power levels
    - AI decides when to use it based on the conversation
    - Returns real-time data from the database
    - This is how AI gets access to live data!
    """
    return await ctx.deps.db.latest_powers(id=ctx.deps.superhero_id)


def print_analysis_result(scenario: str, result):
    """
    📊 RESULTS DISPLAY - Shows the structured output from our AI agent
    Notice how we can access result.output.field_name - this is type-safe!
    """
    print("=" * 80)
    print(f"🦸 SUPERHERO MISSION ANALYSIS")
    print("=" * 80)
    print(f"📋 Scenario: {scenario}")
    print("-" * 80)
    print("📊 ANALYSIS:")
    # Split long text into multiple lines for better readability
    analysis_text = result.output.response_text
    words = analysis_text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= 75:
            current_line += (" " if current_line else "") + word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    for line in lines:
        print(f"   {line}")
    
    print("-" * 80)
    print("⚠️  RECOMMENDATIONS:")
    backup_status = "🆘 CALL FOR BACKUP" if result.output.recommend_backup else "✅ NO BACKUP NEEDED"
    print(f"   Backup Required: {backup_status}")
    
    # Threat level with emoji indicators
    threat_emoji = {
        0: "🟢", 1: "🟢", 2: "🟡", 3: "🟡", 
        4: "🟡", 5: "🟠", 6: "🟠", 7: "🔴", 
        8: "🔴", 9: "🚨", 10: "💀"
    }
    threat_level_emoji = threat_emoji.get(result.output.threat_level, "❓")
    print(f"   Threat Level: {threat_level_emoji} {result.output.threat_level}/10")
    print("=" * 80)
    print()


async def main() -> None:
    # ========================================================================
    # 🚀 RUNNING THE AI AGENT - This is where the magic happens!
    # ========================================================================
    
    # Create dependencies - what the agent needs to work
    deps = SuperheroAnalysisDependencies(superhero_id=42, db=DatabaseConn())  # Spider-Man's ID

    print("🌟 PYDANTIC AI SUPERHERO ANALYSIS SYSTEM 🌟")
    print()

    # ========================================================================
    # 🎯 SCENARIO TESTING - Same agent, different situations
    # ========================================================================
    
    # Scenario 1: High threat situation
    scenario1 = "Facing a massive alien invasion in downtown Manhattan. Energy levels are depleting rapidly."
    result1 = await superhero_agent.run(scenario1, deps=deps)
    print_analysis_result(scenario1, result1)

    # Scenario 2: Low threat situation  
    scenario2 = "Stopped a simple bank robbery. Everything under control."
    result2 = await superhero_agent.run(scenario2, deps=deps)
    print_analysis_result(scenario2, result2)


if __name__ == "__main__":
    asyncio.run(main())