
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
from tools.pubmedbert_tool import pubmedbert_summarize


class ApprovalAgent:
    def __init__(self):
        self.regulatory = RegulatoryTool()

    def run(self, candidate):
        approval_report = self.regulatory.evaluate(candidate)
        # Use PubMedBERT for summarization
        pubmedbert_summary = pubmedbert_summarize(candidate)
        llm_summary = "PubMedBERT summary (top predictions):\n" + "\n".join(pubmedbert_summary)
        return {
            "approval_report": approval_report,
            "llm_summary": llm_summary
        }
