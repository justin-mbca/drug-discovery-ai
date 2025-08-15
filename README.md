
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