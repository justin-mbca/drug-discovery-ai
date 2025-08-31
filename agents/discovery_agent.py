
# agents/discovery_agent.py
"""
Enhancements accomplished in this module:

1. Integrated real PubMed, PubChem, and AlphaFold tools for literature, compound, and structure data.
2. Replaced mock LLM with a local Ollama LLM (configurable model, e.g., llama3).
3. Improved LLM prompt engineering for detailed, context-aware compound summaries.
4. LLM prompt now includes:
    - Readable, formatted PubChem compound information
    - Relevant PubMed IDs for literature context
    - Explicit instructions for summary content (molecular weight, formula, IUPAC name, drug discovery relevance)
5. Streaming LLM output is now fully accumulated for complete responses.
6. Exception handling improved (specific JSON decode errors).
7. LLM model is configurable via the DiscoveryAgent constructor for easy experimentation.
8. Code is modular, maintainable, and ready for further extension.
"""

from tools.pubmed import PubMedTool
from tools.alphafold import AlphaFoldTool
from tools.pubchem import PubChemTool

import requests
import json


def query_llm(prompt, model="llama2"):
    """
    Query a local LLM running via Ollama (http://localhost:11434).
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt},
            timeout=30,
            stream=True
        )
        response.raise_for_status()
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        full_response += data["response"]
                except json.JSONDecodeError:
                    continue
        return full_response.strip() if full_response else "No response from LLM."
    except requests.RequestException as e:
        return f"LLM error: {e}"



class DiscoveryAgent:
    def __init__(self, model="llama3"):
        self.pubmed = PubMedTool()
        self.alphafold = AlphaFoldTool()
        self.pubchem = PubChemTool()
        self.model = model

    def _format_pubchem_info(self, pubchem_info):
        if not pubchem_info or not isinstance(pubchem_info, dict):
            return "No PubChem info available."
        lines = [f"Compound: {pubchem_info.get('compound', 'N/A')}"]
        props = pubchem_info.get('properties', {})
        for k, v in props.items():
            lines.append(f"{k.replace('_', ' ').title()}: {v}")
        return "\n".join(lines)

    def run(self, query):
        literature = self.pubmed.search(query)
        structure = self.alphafold.predict(query)
        pubchem_info = self.pubchem.lookup(query)
        pubchem_str = self._format_pubchem_info(pubchem_info)
        lit_str = ", ".join(literature) if literature else "None"
        prompt = (
            f"Compound information from PubChem:\n{pubchem_str}\n\n"
            f"Relevant PubMed IDs: {lit_str}\n\n"
            "Please provide a detailed summary of the compound, including its molecular weight, formula, IUPAC name, and discuss its potential relevance in drug discovery, referencing the literature if possible."
        )
        llm_summary = query_llm(prompt, model=self.model)
        return {
            "literature": literature,
            "structure": structure,
            "pubchem": pubchem_info,
            "llm_summary": llm_summary
        }
