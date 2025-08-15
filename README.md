
## 🧩 Modular Workflow

The following diagram shows the modular structure and workflow of the project:

```mermaid
graph TD;
	subgraph API Layer
		Main[main.py]
	end
	subgraph Agent Layer
		Crew[agents/multi_agent.py]
	end
	subgraph Tool Layer
		PubMedTool[tools/pubmed.py]
		PubChemTool[tools/pubchem.py]
	end
	subgraph Data Layer
		DB[db/mongodb.py]
		DataRaw[data/raw/]
		DataProcessed[data/processed/]
	end
	subgraph Utils
		UtilsNode[app/utils/]
	end
	Main --> Crew
	Crew --> PubMedTool
	Crew --> PubChemTool
	PubMedTool -->|fetches| DataRaw
	PubChemTool -->|fetches| DataRaw
	Crew --> DB
	Main --> UtilsNode
	Crew --> UtilsNode
	Main -->|returns| Main
```

* API Layer: Handles incoming requests and responses.
* Agent Layer: Orchestrates agent logic and task delegation.
* Tool Layer: Provides modular access to external data sources.
* Data Layer: Handles persistent and intermediate data storage.
* Utils: Shared utility functions used across modules.


# 🧠💊 Drug Discovery AI Assistant

## 🤖 System Overview: LLM RAG Agents & Multi-Agent Orchestration

This project implements an end-to-end LLM-powered system for accelerating pharmaceutical research, leveraging Retrieval-Augmented Generation (RAG) agents and multi-agent workflows:

- **LLM RAG Agents:** The core agents use Retrieval-Augmented Generation (RAG) to combine large language model reasoning with real-time retrieval from biomedical databases (e.g., PubMed, PubChem). This enables up-to-date, context-aware answers for drug discovery tasks.
- **CrewAI Multi-Agent Orchestration:** CrewAI coordinates multiple specialized agents, each responsible for a distinct part of the workflow (e.g., literature search, compound lookup, synthesis). Agents communicate and delegate tasks to maximize research efficiency.
- **Vector Database (MongoDB + VoyageAI):** Retrieved documents and embeddings are stored in MongoDB, with VoyageAI providing vector search capabilities for fast, relevant retrieval.
- **Production API (FastAPI):** The system exposes its capabilities via a FastAPI application, allowing programmatic access to multi-agent LLM workflows for integration with other tools or user interfaces.

**How it works:**
1. A user or API client submits a query (e.g., a compound name) to the FastAPI endpoint.
2. The orchestrator agent (CrewAI) delegates subtasks to RAG agents, which retrieve and synthesize information from external sources using custom tools.
3. Retrieved data is embedded and stored in MongoDB for efficient future access.
4. The system returns a synthesized, context-rich response to the user.

See `agents/multi_agent.py` and `app/main.py` for implementation details.

![Demo GIF](assets/demo.gif) *(record a short Loom/GIF later)*

An end-to-end AI system for accelerating pharmaceutical research, demonstrating:

✅ **LLM Orchestration** (LangChain/CrewAI)  
✅ **Vector RAG** (MongoDB + VoyageAI)  
✅ **Production API** (FastAPI/Pydantic)  
✅ **Multi-Agent Systems**  


## 🏗️ Architecture

The following diagram shows the high-level architecture of the Drug Discovery AI Assistant:

```mermaid
graph TD;
	User[User/API Client]
	subgraph FastAPI App
		Main[main.py]
		Crew[agents/multi_agent.py]
		PubMedTool[tools/pubmed.py]
		PubChemTool[tools/pubchem.py]
	end
	PubMed["PubMed (Online Database)"]
	PubChem["PubChem (Online Database)"]

	User -->|POST /analyze| Main
	Main --> Crew
	Crew --> PubMedTool
	Crew --> PubChemTool
	PubMedTool --> PubMed
	PubChemTool --> PubChem
```

* User/API Client sends a request to the FastAPI app.
* The app orchestrates agents and tools (CrewAI).
* Tools fetch data from online databases (PubMed, PubChem).

---

## 🚀 Quick Start
```bash
pip install -r requirements.txt
python app/main.py