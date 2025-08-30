# agents/discovery_agent.py
from tools.pubmed import PubMedTool
from tools.alphafold import AlphaFoldTool

class DiscoveryAgent:
    def __init__(self):
        self.pubmed = PubMedTool()
        self.alphafold = AlphaFoldTool()

    def run(self, query):
        literature = self.pubmed.search(query)
        structure = self.alphafold.predict(query)
        return {"literature": literature, "structure": structure}
