## 🧩 Modular Workflow

The following diagram shows the modular structure and workflow of the project:


![Modular Workflow Diagram](assets/workflow_diagram.png)

* API Layer: Handles incoming requests and responses.
* Agent Layer: Orchestrates agent logic and task delegation.
* Tool Layer: Provides modular access to external data sources and AI models.
* Data Layer: Handles persistent and intermediate data storage.
* Utils: Shared utility functions used across modules.


# 🧠💊 Drug Discovery AI Assistant


## 🤖 System Overview: LLM RAG Agents & Multi-Agent Orchestration

This project is an end-to-end AI platform for accelerating pharmaceutical research, built on modular Retrieval-Augmented Generation (RAG) agents and a multi-agent workflow:

- **LLM RAG Agents:** Specialized agents combine large language model reasoning with real-time retrieval from biomedical databases (e.g., PubMed, PubChem), enabling up-to-date, context-aware answers for drug discovery tasks.
- **Multi-Agent Orchestration:** A custom orchestrator coordinates multiple agents, each handling a distinct stage of the workflow (e.g., literature search, compound design, validation, approval). Agents communicate and delegate tasks to maximize research efficiency.
- **Vector Database (MongoDB + VoyageAI):** Retrieved documents and embeddings are stored in MongoDB, with VoyageAI providing vector search for fast, relevant retrieval.
- **Production API (FastAPI):** The system exposes its capabilities via a FastAPI application, enabling programmatic access to the multi-agent workflow for integration with other tools or user interfaces.

**Workflow Overview:**
1. A user or API client submits a query (e.g., a compound name) to the FastAPI endpoint.
2. The orchestrator agent delegates subtasks to specialized RAG agents, which retrieve and synthesize information from external sources using modular tools.
3. Retrieved and generated data are embedded and stored in MongoDB for efficient future access.
4. The system returns a synthesized, context-rich response to the user.

See `agents/multi_agent.py` and `app/main.py` for implementation details.

![Demo GIF](assets/demo.gif) *(record a short Loom/GIF later)*

An end-to-end AI system for accelerating pharmaceutical research, demonstrating:

✅ **LLM Orchestration** (LangChain/CrewAI)  
✅ **Vector RAG** (MongoDB + VoyageAI)  
✅ **Production API** (FastAPI/Pydantic)  
✅ **Multi-Agent Systems**  



## 🏗️ Architecture

The following diagram shows the updated high-level architecture of the Drug Discovery AI Assistant:



![Architecture Diagram](assets/architecture_diagram.png)

* User/API Client sends a request to the FastAPI app.
* The app orchestrates agents and tools.
* Each agent delegates to specialized tools for data retrieval and analysis.
* Tools fetch data from online databases or perform computations.
* All results and intermediate data are stored in MongoDB.

## 🧑‍🔬 Agent Descriptions & AI Methods

| Agent            | Description                                                                 | AI Methods/Models Used                |
|------------------|-----------------------------------------------------------------------------|--------------------------------------|
| Discovery Agent  | Searches biomedical literature and databases to identify potential drug candidates. | LLM (RAG), PubMed, PubChem           |
| Design Agent     | Designs and optimizes candidate compounds based on discovery results.             | LLM, AlphaFold, Docking, QSAR        |
| Validation Agent | Validates candidate compounds using lab and clinical data.                        | LLM, LabTool, ClinicalTool           |
| Approval Agent   | Assesses regulatory requirements and prepares documentation for approval.         | LLM, RegulatoryTool                  |

---

## 🚀 Quick Start
```bash
pip install -r requirements.txt
uvicorn app.example_main:app --reload
```

## 🧪 Example API Endpoints

Test the full workflow (all stages):

```
GET /full_workflow?query=BACE1
```

Test individual stages:

```
GET /discovery?query=BACE1
GET /design?compound=aspirin
GET /validation?candidate=aspirin
GET /approval?candidate=aspirin
```

You can also use the interactive docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to try all endpoints in your browser.
