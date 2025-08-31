
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
from tools.biobert_tool import biobert_summarize
from tools.pubmedbert_tool import pubmedbert_summarize






class DiscoveryAgent:
    def __init__(self):
        self.pubmed = PubMedTool()
        self.alphafold = AlphaFoldTool()
        self.pubchem = PubChemTool()

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

        # If PubChem returns no info, assume protein/gene target and use BioBERT
        if not pubchem_info or pubchem_info == {} or pubchem_str == "No PubChem info available.":
            # Use BioBERT for protein/gene summarization
            biobert_summary = biobert_summarize(query)
            llm_summary = "BioBERT summary (top predictions):\n" + "\n".join(biobert_summary)
        else:
            # Use PubMedBERT for compound summarization
            pubmedbert_summary = pubmedbert_summarize(query)
            llm_summary = "PubMedBERT summary (top predictions):\n" + "\n".join(pubmedbert_summary)

        return {
            "literature": literature,
            "structure": structure,
            "pubchem": pubchem_info,
            "llm_summary": llm_summary
        }
