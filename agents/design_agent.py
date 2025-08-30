# agents/design_agent.py
from tools.pubchem import PubChemTool
from tools.docking import DockingTool
from tools.qsar import QSARTool

class DesignAgent:
    def __init__(self):
        self.pubchem = PubChemTool()
        self.docking = DockingTool()
        self.qsar = QSARTool()

    def run(self, compound):
        compound_info = self.pubchem.lookup(compound)
        docking_result = self.docking.screen(compound)
        qsar_result = self.qsar.predict(compound)
        return {
            "compound_info": compound_info,
            "docking_result": docking_result,
            "qsar_result": qsar_result
        }
