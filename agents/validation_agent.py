# agents/validation_agent.py
from tools.lab import LabTool
from tools.clinical import ClinicalTool

class ValidationAgent:
    def __init__(self):
        self.lab = LabTool()
        self.clinical = ClinicalTool()

    def run(self, candidate):
        lab_result = self.lab.test(candidate)
        clinical_result = self.clinical.trial(candidate)
        return {
            "lab_result": lab_result,
            "clinical_result": clinical_result
        }
