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
		PredictiveModeling[predictive_modeling.py]
		DoE[doe_example.py]
		RegulatoryNLP[regulatory_nlp.py]
	end
	subgraph Data Layer
		DB[db/mongodb.py]
		SQLDB[drug_discovery.db]
		DataRaw[data/raw/]
		DataProcessed[data/processed/]
	end
	subgraph Utils
		UtilsNode[app/utils/]
	end
	Main --> Crew
	Crew --> PubMedTool
	Crew --> PubChemTool
	Crew --> PredictiveModeling
	Crew --> DoE
	Crew --> RegulatoryNLP
	PubMedTool -->|fetches| DataRaw
	PubChemTool -->|fetches| DataRaw
	Crew --> DB
	Crew --> SQLDB
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



## 🚀 API Endpoints & Usage

### Base URL

```
http://127.0.0.1:8000
```

### Endpoints

#### `GET /`
Returns a welcome message to confirm the API is running.

**Example Response**
```json
{
	"message": "Drug Discovery AI API"
}
```

---

#### `POST /analyze`
Analyze a chemical compound using the AI agents.

**Request Body**
```json
{
	"compound": "aspirin"
}
```

**Example Curl**
```bash
curl -X POST "http://127.0.0.1:8000/analyze" -H "Content-Type: application/json" -d '{"compound": "aspirin"}'
```

**Example Response**
```json
{
	"compound": "aspirin",
	"properties": {
		"molecular_weight": 123.45,
		"formula": "C6H12O6",
		"iupac_name": "glucose"
	},
	"source": "mock"
}
```

---

### Interactive API Documentation

After starting the app, open your browser and visit:

- [Swagger UI](http://127.0.0.1:8000/docs) — interactive API docs and testing
- [ReDoc](http://127.0.0.1:8000/redoc) — alternative API documentation

---

### Example Screenshot

Add a screenshot of your Swagger UI here for reference:


[View API Docs](https://github.com/justin-mbca/drug-discovery-ai/blob/main/docs/api-docs.pdf)


---

### How to Run

1. Install dependencies:
	 ```bash
	 pip install -r requirements.txt
	 ```

2. Set your OpenAI API key in a `.env` file:
	 ```
	 OPENAI_API_KEY=sk-...
	 ```

3. Start the app:
	 ```bash
	 uvicorn app.main:app --reload
	 ```

4. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

---

### Example Compounds

Try these in the `/analyze` endpoint:
- `"aspirin"`
- `"glucose"`
- `"ibuprofen"`
- `"acetaminophen"`

---

The following diagram shows the high-level architecture of the Drug Discovery AI Assistant:

```mermaid
graph TD;
	User[User/API Client]
	subgraph FastAPI App
		Main[main.py]
		Crew[agents/multi_agent.py]
		PubMedTool[tools/pubmed.py]
		PubChemTool[tools/pubchem.py]
		PredictiveModeling[predictive_modeling.py]
		DoE[doe_example.py]
		RegulatoryNLP[regulatory_nlp.py]
	end
	PubMed["PubMed (Online Database)"]
	PubChem["PubChem (Online Database)"]
	SQLDB["SQLite DB"]
	MongoDB["MongoDB"]

	User -->|POST /analyze| Main
	Main --> Crew
	Crew --> PubMedTool
	Crew --> PubChemTool
	Crew --> PredictiveModeling
	Crew --> DoE
	Crew --> RegulatoryNLP
	PubMedTool --> PubMed
	PubChemTool --> PubChem
	Crew --> SQLDB
	Crew --> MongoDB
```

* User/API Client sends a request to the FastAPI app.
* The app orchestrates agents and tools (CrewAI).
* Tools fetch data from online databases (PubMed, PubChem).

---

## 🆕 Additional Features

### 1. Predictive Modeling (scikit-learn)
Train a machine learning model to predict compound properties (e.g., solubility) from features.

**Example:**
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pandas as pd

df = pd.read_csv('data/compound_features.csv')
X = df.drop('solubility', axis=1)
y = df['solubility']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestRegressor()
model.fit(X_train, y_train)
preds = model.predict(X_test)
print("MSE:", mean_squared_error(y_test, preds))
```

### 2. SQL/Database Integration (SQLite)
Store and query compound or experiment data using SQLite.

**Example:**
```python
import sqlite3
conn = sqlite3.connect('drug_discovery.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS compounds (id INTEGER PRIMARY KEY, name TEXT, property REAL)''')
c.execute("INSERT INTO compounds (name, property) VALUES (?, ?)", ("aspirin", 123.45))
conn.commit()
for row in c.execute("SELECT * FROM compounds"):
    print(row)
conn.close()
```

### 3. Design of Experiments (DoE)
Generate a factorial design matrix for formulation experiments using pure Python and pandas.

**Example:**
```python
import pandas as pd
import itertools
levels_A = [0, 1, 2]  # Excipient A: low, medium, high
levels_B = [0, 1, 2]  # Excipient B: low, medium, high
factorial_design = list(itertools.product(levels_A, levels_B))
df = pd.DataFrame(factorial_design, columns=['Excipient_A', 'Excipient_B'])
print(df)
```

### 4. Regulatory/Clinical Data Workflow (NLP)
Parse and analyze regulatory or clinical trial summaries for keywords (e.g., FDA) using pandas and regex.

**Example:**
```python
import pandas as pd
import re
df = pd.read_csv('data/clinical_trials.csv')
df['has_fda'] = df['summary'].apply(lambda x: bool(re.search(r'FDA', x, re.I)))
print(df[['trial_id', 'has_fda']])
```