# AI Academic Advisor — Persistent Memory & MCP Server

## Overview

The **AI Academic Advisor** project implements a persistent, intelligent backend designed using the Model Context Protocol (MCP) pattern. Its primary goal is to empower AI agents with long-term conversational memory and semantic contextual awareness. 

Instead of relying solely on a language model's immediate context window, this server acts as an external brain. It utilizes a dual-database architecture to safely store user conversations, academic milestones, and user preferences into relational memory, while seamlessly mirroring that conversational data into a highly-performant vector database for semantic retrieval. This enables an AI Academic Advisor to instantly recall past advice, prerequisite information, and student interests regardless of how much time has passed.

## Tech Stack

This project is built using modern, production-grade Python tooling:
- **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Async web server & routing)
- **Data Validation:** [Pydantic v2](https://docs.pydantic.dev/latest/) (Strict typing & schemas)
- **Relational Database:** [SQLite](https://www.sqlite.org/) + [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (ORM)
- **Vector Database:** [ChromaDB](https://www.trychroma.com/) (Semantic Search)
- **Embeddings:** [Sentence-Transformers](https://sbert.net/) (`all-MiniLM-L6-v2`)
- **Containerization:** [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

## Architecture Detail

The architecture resolves around three primary layers (Memory, Control, and Process):

```text
┌────────────────────────────────────────────────────────┐
│                   MCP Server Backend                   │
│                                                        │
│  ┌────────────────┐ ┌────────────────┐ ┌─────────────┐ │
│  │  memory_write  │ │  memory_read   │ │   memory_   │ │
│  │   (Tool 1)     │ │   (Tool 2)     │ │  retrieve   │ │
│  └───────┬────────┘ └───────┬────────┘ └─────┬───────┘ │
│          │                  │                │         │
│     ┌────▼─────┐       ┌────▼─────┐     ┌────▼─────┐   │
│     │  SQLite  │       │  SQLite  │     │ ChromaDB │   │
│     │ + Chroma │       │   Only   │     │   Only   │   │
│     └──────────┘       └──────────┘     └──────────┘   │
└────────────────────────────────────────────────────────┘
```

1. **Control Layer (FastAPI):** Exposes HTTP REST boundaries, defining precise, explicit schemas (`session_id`, `role`, `content`) for safe external interaction.
2. **Process Layer (Tools):** Modular functionality handlers representing specific agent "capabilities", such as writing or semantically querying specific memory segments.
3. **Memory Layer (Dual Storage):** 
   - **SQLite** guarantees strict referential integrity, sequential historical logs, profiles, and milestones.
   - **ChromaDB** parses conversations, converts them to embeddings on the fly, and places them in multi-dimensional space, solving context issues through contextual similarity queries rather than chronological sorting.

## Project Structure

```text
d:\GPP\Vector Search\
├── mcp_server/              # Core Application Source
│   ├── __init__.py          
│   ├── main.py              # FastAPI app definition, routing, and lifecycle hooks
│   ├── database.py          # SQLAlchemy engine creation and local initialization
│   ├── models.py            # Relational ORM models (Conversation, Preferences, Milestones)
│   ├── memory_schemas.py    # Request/Response data validation definitions
│   ├── vector_store.py      # ChromaDB configuration and vector operations
│   └── tools/               # Modular Tool Actions Directory
│       ├── __init__.py 
│       ├── memory_write.py  # Handle writing to both databases concurrently
│       ├── memory_read.py   # Secure chronological read retrieval
│       └── memory_retrieve.py # Vector semantic proximity search
├── docker-compose.yml       # Configuration for deploying containerized environments
├── .env.example             # Configuration templates
├── submission.json          # Project metadata
└── README.md                # Documentation
```

## Setup Instructions

### Environment Setup

1. **Clone the repository:** Ensure you are in the project root directory (`d:/GPP/Vector Search`).
2. **Setup environment variables:** Create your local `.env` file from the example.
```bash
cp .env.example .env
```

The core configurable variables inside `.env` include:
| Variable | Default Value | Description |
|----------|---------------|-------------|
| `MCP_PORT` | `8080` | Port the web service exposes |
| `DATABASE_URL` | `sqlite:///./data/academic_advisor.db` | Target relational persistence |
| `CHROMA_PERSISTENT` | `true` | Ensure memory survives reboots |
| `CHROMA_PERSIST_DIR` | `./data/chroma` | Target vector persistence |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Transformer model for embeddings |

## How to Run the Application

### Method 1: Using Docker (Highly Recommended)
Docker completely abstracts the Python environment, dependencies, and complex C++ build tools required by ChromaDB and the HuggingFace architectures.

1. **Build and spin up the containers:**
```bash
docker-compose up --build -d
```
2. **Check the logs & health:**
```bash
docker-compose logs -f
curl http://localhost:8080/health
```

### Method 2: Running Locally (Native OS)
If you prefer to run it bare-metal, ensure you have Python 3.11+ and a C++ compiler installed locally.

1. **Install dependencies:**
```bash
cd mcp_server
pip install -r requirements.txt
```
2. **Start the Uvicorn webserver:**
```bash
uvicorn mcp_server.main:app --host 0.0.0.0 --port 8080 --reload
```

## Verifying Setup

Once the server is running on `8080`, test your dual-write semantic layer securely via curl:

**1. Store a memory (Write)**
```bash
curl -X POST http://localhost:8080/memory/write \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_session_1",
    "role": "user",
    "content": "I am interested in specializing in Artificial Intelligence and Machine Learning next semester."
  }'
```

**2. Query by Semantic Meaning (Retrieve)**
```bash
curl -X POST http://localhost:8080/memory/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does the user want to specialize in?",
    "top_k": 3
  }'
```
You should successfully see the system extract your exact previously written conversation context!
