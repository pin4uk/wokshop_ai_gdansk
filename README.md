# 🤖 AI Agent Evolution Workshop - Gdansk

A comprehensive workshop demonstrating the evolution from simple AI responses to sophisticated agents with knowledge graph memory.

## 🎯 Workshop Overview

This workshop takes you through 5 progressive steps of AI agent development:

1. **🧠 Pydantic AI Fundamentals** - Structured AI responses with validation
2. **📚 Basic RAG System** - Document retrieval and generation
3. **🔧 Pydantic AI + RAG** - Intelligent agents with retrieval tools
4. **🕸️ Knowledge Graphs** - Graph-based memory with Neo4j
5. **🎉 Final Integration** - AI agents with persistent graph memory

## 🛠️ Prerequisites & Installation

### System Requirements
- Python 3.9+
- Neo4j Database
- PostgreSQL Database (or Neon.tech account)
- OpenAI API Key

### 1. Clone and Setup Python Environment

```bash
git clone <repository-url>
cd wokshop_ai_gdansk

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### 2. Install Dependencies

Each workshop step has its own requirements. Install them progressively or all at once:

```bash
# Step 1: Pydantic AI basics
cd pydantic-ai-quickstart
pip install -r requirements.txt

# Step 2 & 3: RAG systems
cd ../basic-rag
pip install -r requirements.txt

cd ../pydantic-ai-rag  
pip install -r requirements.txt

# Step 4 & 5: Knowledge graphs
cd ../pydantic-graphiti
pip install -r requirements.txt

# Or install everything at once from project root:
cd ..
pip install -r pydantic-ai-quickstart/requirements.txt
pip install -r basic-rag/requirements.txt  
pip install -r pydantic-ai-rag/requirements.txt
pip install -r pydantic-graphiti/requirements.txt
```

### 3. Database Setup

#### Option A: Neon.tech (Recommended for Simplicity)

1. Go to [neon.tech](https://neon.tech) and create a free account
2. Create a new project
3. Copy the connection string from the dashboard
4. Use this as your `DATABASE_URL` in `.env`

#### Option B: Local PostgreSQL

```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql
brew services start postgresql

# Create database
createdb workshop_rag

# Your DATABASE_URL will be:
# DATABASE_URL=postgresql://username:password@localhost:5432/workshop_rag
```

#### Neo4j Setup

**Option A: Neo4j Desktop (Recommended)**
1. Download [Neo4j Desktop](https://neo4j.com/download/)
2. Create a new project and database
3. Set password and start the database
4. Use connection details in `.env`

**Option B: Docker**
```bash
docker run \
    --name neo4j-workshop \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -e NEO4J_AUTH=neo4j/your-password \
    neo4j:latest
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# PostgreSQL Database (for RAG steps)
DATABASE_URL=postgresql://username:password@host:port/database
# Example for Neon.tech:
# DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# Neo4j Database (for graph steps)  
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password

# Optional: Model configuration
MODEL_CHOICE=gpt-4o-mini
```

### 5. API Keys Setup

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create account and add billing information
3. Generate API key in API Keys section
4. Add to `.env` file

## 📁 Workshop Structure

### Step 1: `pydantic-ai-quickstart/` 
**🧠 Learn Pydantic AI Fundamentals**

```
pydantic-ai-quickstart/
├── marvel_superhero_analysis.py    # Main demo script
├── requirements.txt                # pydantic-ai, openai
└── README.md                      # Step-specific instructions
```

**What you'll learn:**
- Structured AI outputs with Pydantic validation
- Agent tools and dynamic system prompts
- Type-safe AI responses
- Basic agent architecture patterns

**Run the demo:**
```bash
cd pydantic-ai-quickstart
python marvel_superhero_analysis.py
```

### Step 2: `basic-rag/`
**📚 Build a RAG System from Scratch**

```
basic-rag/
├── rag.py                 # Main RAG pipeline
├── retriever.py           # Vector similarity search  
├── ingest.py             # Data ingestion script
├── db.py                 # Database connection utilities
├── requirements.txt      # Dependencies
└── data/
    └── doc1.md          # Sample MCU documents
```

**What you'll learn:**
- Document chunking and embedding
- Vector similarity search (cosine similarity)
- RAG pipeline: Retrieve → Augment → Generate
- PostgreSQL for vector storage

**Setup and run:**
```bash
cd basic-rag

# First: Ingest documents into database
python ingest.py --reset

# Then: Run RAG queries
python rag.py "Who is Iron Man?"
```

### Step 3: `pydantic-ai-rag/`
**🔧 Combine AI Agents with RAG Tools**

```
pydantic-ai-rag/
├── agent_rag.py          # AI agent with RAG tools
├── retriever.py          # Reusable retriever component
├── ingest.py             # Data ingestion  
├── db.py                 # Database utilities
├── requirements.txt      # Dependencies
└── data/                 # Mission briefing documents
    ├── covert_network.md
    ├── hydra_tech_facility.md
    ├── rogue_enhanced.md
    ├── supernatural_threat.md
    └── urban_invasion.md
```

**What you'll learn:**
- RAG as agent tools (not standalone pipeline)
- Multiple data sources in one agent
- Intelligent tool selection by AI
- Mission intelligence analysis system

**Setup and run:**
```bash
cd pydantic-ai-rag

# Ingest mission documents
python ingest.py --reset

# Run intelligent mission analyst
python agent_rag.py
```

### Step 4: `basic-graphiti/`
**🕸️ Knowledge Graphs with Neo4j**

```
basic-graphiti/
├── quickstart.py         # Graphiti knowledge graph demo
├── ingest.py            # Episode ingestion
├── clear_db.py          # Database cleanup utility
├── episodes.json        # MCU story episodes
└── requirements.txt     # graphiti-core, neo4j
```

**What you'll learn:**
- Knowledge graphs vs. vector databases
- Entity extraction and relationships
- Temporal knowledge (facts with time validity)
- Graph-based search and discovery

**Setup and run:**
```bash
cd basic-graphiti

# Clear any existing data
python clear_db.py

# Ingest MCU episodes into knowledge graph  
python ingest.py

# Explore graph-based knowledge
python quickstart.py
```

### Step 5: `pydantic-graphiti/`
**🎉 Ultimate AI Agent with Graph Memory**

```
pydantic-graphiti/
├── agent.py             # Final integration demo
├── ingest.py            # Knowledge graph ingestion
└── requirements.txt     # All dependencies
```

**What you'll learn:**
- AI agents with persistent knowledge graphs
- Conversational memory within sessions
- Temporal reasoning ("Is Tony Stark alive?")
- Production-ready AI agent architecture

**Setup and run:**
```bash
cd pydantic-graphiti

# Load MCU knowledge into graph
python ingest.py

# Chat with AI agent that has graph memory
python agent.py
```
