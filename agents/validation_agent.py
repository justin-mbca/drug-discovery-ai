
# agents/validation_agent.py
"""
ValidationAgent enhancements:
1. Integrates real Lab and Clinical tools.
2. Adds LLM summarization using local Ollama (configurable model).
3. Formats prompt for readability and context.
4. Accumulates full streamed LLM output.
5. Model is configurable via constructor.
6. Modular and ready for extension.
"""

from tools.lab import LabTool
from tools.clinical import ClinicalTool
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

class ValidationAgent:
    def __init__(self, model="llama3"):
        self.lab = LabTool()
        self.clinical = ClinicalTool()
        self.model = model

    def run(self, candidate):
        lab_result = self.lab.test(candidate)
        clinical_result = self.clinical.trial(candidate)
        prompt = (
            f"Lab result: {lab_result}\n\n"
            f"Clinical trial result: {clinical_result}\n\n"
            "Please provide a detailed summary of the candidate's validation, including interpretation of lab and clinical results, and discuss the implications for further development."
        )
        llm_summary = query_llm(prompt, model=self.model)
        return {
            "lab_result": lab_result,
            "clinical_result": clinical_result,
            "llm_summary": llm_summary
        }
