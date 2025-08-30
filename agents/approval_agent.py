# agents/approval_agent.py
from tools.regulatory import RegulatoryTool

class ApprovalAgent:
    def __init__(self):
        self.regulatory = RegulatoryTool()

    def run(self, candidate):
        approval_report = self.regulatory.evaluate(candidate)
        return {"approval_report": approval_report}
