## 🎯 Drug Target Discovery Pipeline

### Key Capabilities
- **Disease-to-Target Extraction** using BioBERT NER
- **Network-Based Target Prioritization** using GNNs
- **Automated Compound Retrieval** from ChEMBL

| Disease          | Demonstrated Examples                       |
|------------------|--------------------------------------------|
| Parkinson's      | Example 1, Example 2                      |
| Alzheimer's      | Example 1, Example 2                      |
| ALS              | Example 1, Example 2                      |
| Pancreatic Cancer| Example 1, Example 2                      |

### Try It Yourself
**Curl Example:**
```bash
curl -X POST https://api.example.com/discover -d '{"disease": "Parkinson's"}'
```

**Python Example:**
```python
import requests
response = requests.post('https://api.example.com/discover', json={'disease': 'Parkinson's'})
print(response.json())
```

### Sample JSON Output
```json
{
  "suggested_targets": ["Target1", "Target2"],
  "network_scores": [0.9, 0.75]
}
```

### Technologies Used
- BioBERT
- PubMedBERT
- PyTorch Geometric
- KEGG
- ChEMBL

### Architecture Flowchart
(Disease Input → PubMed Query → BioBERT NER → Target Candidates → Network Construction → GNN Analysis → ChEMBL Compound Retrieval → Multi-Agent Evaluation)