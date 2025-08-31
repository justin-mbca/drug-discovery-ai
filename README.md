

# Supported Biomedical Language Models

All agents now use only biomedical-specific language models for summarization and knowledge extraction. General-purpose LLMs (Llama, Mistral, Phi3, etc.) and Ollama integration have been removed for simplicity and domain focus.

## Biomedical Models Used

- **BioGPT**: Microsoft’s biomedical language model, trained on PubMed and biomedical text. Excellent for drug/life sciences tasks, and highly recommended for biomedical text generation, summarization, and question answering.
- **PubMedBERT**: Biomedical BERT model, trained on PubMed abstracts and full text. Ideal for extracting biomedical knowledge, masked word prediction, and summarization of scientific literature.
- **BioBERT**: Biomedical BERT variant, also trained on PubMed and PMC articles. Used for protein/gene target summarization and biomedical fill-mask tasks.

> **Note:** All models are loaded via Hugging Face Transformers and run locally. No Ollama or general LLMs are required.

**When to use these models:**
- Use **BioGPT**, **PubMedBERT**, or **BioBERT** for all drug discovery, pharmaceutical, or life sciences tasks (e.g., drug properties, disease mechanisms, literature summarization, biomedical Q&A).
- These models are trained on domain-specific corpora (PubMed, biomedical literature), so they produce more accurate, relevant, and trustworthy results for scientific and medical queries than general LLMs.

See the `tools/biobert_tool.py` and `tools/pubmedbert_tool.py` for usage examples.


# Agent Enhancements (August 2025)

All core agents (Discovery, Design, Validation, Approval) have been modernized and enhanced:

- Integrated real data sources and tools for each agent (PubMed, PubChem, AlphaFold, Docking, QSAR, Lab, Clinical, Regulatory).
- Added biomedical LLM summarization to every agent using BioGPT, PubMedBERT, or BioBERT.
- Prompts are now readable, context-rich, and tailored to each agent's domain (compound info, literature, docking, QSAR, lab, clinical, regulatory, etc.).
- Summarization is performed using domain-specific models for high-quality, relevant responses.
- Exception handling is robust and specific.
- Code is modular, maintainable, and ready for further extension.


# Recent Enhancements (August 2025)

The drug discovery AI workflow has been significantly improved:

- Integrated real PubMed, PubChem, and AlphaFold tools for literature, compound, and structure data.
- All summarization and knowledge extraction now use biomedical-specific models (BioGPT, PubMedBERT, BioBERT).
- Prompts and fill-mask tasks are tailored for biomedical context and accuracy.
- Exception handling is more robust and specific.
- Code is modular, maintainable, and ready for further extension.

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


## 🖼️ Example Workflow & LLM Outputs (Mermaid Diagram)

```mermaid
flowchart TD
	A[Discovery Agent] -->|BioGPT| B1["Aspirin is a nonsteroidal anti-inflammatory drug (NSAID)..."]
	A -->|PubMedBERT| B2["aspirin is used to treat atherosclerosis."]
	C[Design Agent] -->|PubMedBERT| D["Docking score for compound X is -8.2..."]
	E[Validation Agent] -->|PubMedBERT| F["Lab results confirm efficacy in vitro..."]
	G[Approval Agent] -->|PubMedBERT| H["Regulatory summary: meets FDA requirements..."]

	style A fill:#e0f7fa,stroke:#00796b,stroke-width:2px
	style C fill:#fff3e0,stroke:#f57c00,stroke-width:2px
	style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
	style G fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
```

*This diagram shows each agent and the biomedical model used for summarization. All stages now use BioGPT, PubMedBERT, or BioBERT as appropriate.*

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


---

## 🏁 What Next?

Now that you have the Drug Discovery AI Assistant running locally, here are some suggested next steps:

- **Customize Agents:** Modify or extend the agent logic in `agents/` to add new tools, change prompts, or integrate additional data sources.
- **Integrate New Models:** Try other LLMs from Ollama or Hugging Face by updating the agent `model` parameter, or add your own domain-specific models.
- **Experiment with Prompts:** Tune the prompts for each agent to improve the quality and relevance of LLM outputs for your specific research needs.
- **Deploy the API:** Use FastAPI’s deployment options to run the system in production (e.g., with Docker, on a cloud VM, or behind a reverse proxy).
- **Connect a Frontend:** Build a web or desktop UI to interact with the API, visualize results, or manage workflows.
- **Scale Up:** Integrate with more advanced vector databases, distributed compute, or workflow orchestration tools for larger-scale research.
- **Contribute:** Open issues or pull requests to help improve the project, or share your use cases and feedback!


---

## 🌐 Connecting a Frontend UI

You can build a user-friendly frontend to interact with the Drug Discovery AI API. Here are some options and examples:

### 1. Simple Web Client (HTML/JS)

You can use a basic HTML/JavaScript page to send requests to the FastAPI backend:

```html
<form id="queryForm">
	<input type="text" id="query" placeholder="Enter compound name">
	<button type="submit">Submit</button>
</form>
<pre id="result"></pre>
<script>
document.getElementById('queryForm').onsubmit = async function(e) {
	e.preventDefault();
	const q = document.getElementById('query').value;
	const res = await fetch(`http://127.0.0.1:8000/full_workflow?query=${encodeURIComponent(q)}`);
	document.getElementById('result').textContent = await res.text();
};
</script>
```

### 2. Streamlit App (Python)

Create a simple Streamlit UI for local use:

```python
import streamlit as st
import requests

st.title("Drug Discovery AI Assistant")
query = st.text_input("Enter compound name:")
if st.button("Submit"):
		response = requests.get(f"http://127.0.0.1:8000/full_workflow?query={query}")
		st.write(response.text)
```

### 3. Advanced Web UI (React, Next.js, etc.)

For a modern, user-friendly experience, build a custom frontend using React, Next.js, or similar frameworks. Example (React fetch call):

```javascript
fetch('http://127.0.0.1:8000/full_workflow?query=BACE1')
	.then(res => res.json())
	.then(data => setResult(data));
```

You can design interactive dashboards, result visualizations, and workflow management features tailored to your needs.


---

## 🧪 Step-by-Step Example: Discovering a Drug Candidate

Here’s how you can use the Drug Discovery AI pipeline for a real-world drug discovery scenario:

**Goal:** Identify and evaluate new drug candidates for Alzheimer’s disease (target: BACE1)

### 1. Start the Backend API
```bash
uvicorn app.example_main:app --reload
```

### 2. Submit a Query (e.g., via browser or curl)
```bash
curl "http://127.0.0.1:8000/full_workflow?query=BACE1"
```
Or use the interactive docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Review the Output
- **Discovery Agent:** Summarizes BACE1’s role in Alzheimer’s, retrieves relevant compounds and literature.
- **Design Agent:** Suggests and evaluates new compound designs, docking scores, and predicted properties.
- **Validation Agent:** Simulates lab/clinical validation, summarizes findings.
- **Approval Agent:** Generates a regulatory summary for the candidate.

### 4. Iterate and Refine
- Try different targets or compounds (e.g., "aspirin", "tau protein").
- Adjust agent prompts or models for more specific results.
- Integrate your own data or tools for deeper analysis.

### 5. (Optional) Build a Frontend
- Use the provided examples to create a web UI for easier interaction and visualization.

