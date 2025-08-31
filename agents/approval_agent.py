
# agents/approval_agent.py
"""
ApprovalAgent enhancements:
1. Integrates real Regulatory tool.
2. Adds LLM summarization using local Ollama (configurable model).
3. Formats prompt for readability and context.
4. Accumulates full streamed LLM output.
5. Model is configurable via constructor.
6. Modular and ready for extension.
"""

from tools.regulatory import RegulatoryTool
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

class ApprovalAgent:
    def __init__(self, model="llama3"):
        self.regulatory = RegulatoryTool()
        self.model = model

    def run(self, candidate):
        approval_report = self.regulatory.evaluate(candidate)
        prompt = (
            f"Regulatory approval report: {approval_report}\n\n"
            "Please provide a detailed summary of the regulatory approval status, highlight any deficiencies or required actions, and discuss the next steps for bringing this candidate to market."
        )
        llm_summary = query_llm(prompt, model=self.model)
        return {
            "approval_report": approval_report,
            "llm_summary": llm_summary
        }
