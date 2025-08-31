
# agents/design_agent.py
"""
DesignAgent enhancements:
1. Integrates real PubChem, Docking, and QSAR tools.
2. Adds LLM summarization using local Ollama (configurable model).
3. Formats prompt for readability and context.
4. Accumulates full streamed LLM output.
5. Model is configurable via constructor.
6. Modular and ready for extension.
"""

from tools.pubchem import PubChemTool
from tools.docking import DockingTool
from tools.qsar import QSARTool
import requests
import json

def query_llm(prompt, model="llama3"):
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

class DesignAgent:
    def __init__(self, model="llama3"):
        self.pubchem = PubChemTool()
        self.docking = DockingTool()
        self.qsar = QSARTool()
        self.model = model

    def _format_compound_info(self, compound_info):
        if not compound_info or not isinstance(compound_info, dict):
            return "No PubChem info available."
        lines = [f"Compound: {compound_info.get('compound', 'N/A')}"]
        props = compound_info.get('properties', {})
        for k, v in props.items():
            lines.append(f"{k.replace('_', ' ').title()}: {v}")
        return "\n".join(lines)

    def run(self, compound):
        compound_info = self.pubchem.lookup(compound)
        docking_result = self.docking.screen(compound)
        qsar_result = self.qsar.predict(compound)
        compound_str = self._format_compound_info(compound_info)
        prompt = (
            f"Compound information from PubChem:\n{compound_str}\n\n"
            f"Docking result: {docking_result}\n\n"
            f"QSAR prediction: {qsar_result}\n\n"
            "Please provide a detailed summary of this compound's design and optimization potential, referencing docking and QSAR results."
        )
        llm_summary = query_llm(prompt, model=self.model)
        return {
            "compound_info": compound_info,
            "docking_result": docking_result,
            "qsar_result": qsar_result,
            "llm_summary": llm_summary
        }
