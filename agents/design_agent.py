
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
from tools.pubmedbert_tool import pubmedbert_summarize


class DesignAgent:
    def __init__(self):
        self.pubchem = PubChemTool()
        self.docking = DockingTool()
        self.qsar = QSARTool()

    def _format_compound_info(self, compound_info):
        if not compound_info or not isinstance(compound_info, dict):
            return "No PubChem info available."
        lines = [f"Compound: {compound_info.get('compound', 'N/A')}"]
        props = compound_info.get('properties', {})
        for k, v in props.items():
            lines.append(f"{k.replace('_', ' ').title()}: {v}")
        return "\n".join(lines)

    def run(self, compound, compounds_for_target=None):
        results = []
        # If a list of compounds is provided (from target lookup), analyze each
        if compounds_for_target and isinstance(compounds_for_target, list) and len(compounds_for_target) > 0:
            for c in compounds_for_target:
                cid = c.get("cid")
                name = c.get("iupac_name") or str(cid)
                compound_info = self.pubchem.lookup(name)
                docking_result = self.docking.screen(name)
                qsar_result = self.qsar.predict(name)
                pubmedbert_summary = pubmedbert_summarize(name)
                llm_summary = "PubMedBERT summary (top predictions):\n" + "\n".join(pubmedbert_summary)
                results.append({
                    "compound": name,
                    "cid": cid,
                    "compound_info": compound_info,
                    "docking_result": docking_result,
                    "qsar_result": qsar_result,
                    "llm_summary": llm_summary
                })
            return {"analyzed_compounds": results}
        # Otherwise, fallback to single compound as before
        compound_info = self.pubchem.lookup(compound)
        docking_result = self.docking.screen(compound)
        qsar_result = self.qsar.predict(compound)
        pubmedbert_summary = pubmedbert_summarize(compound)
        llm_summary = "PubMedBERT summary (top predictions):\n" + "\n".join(pubmedbert_summary)
        return {
            "compound_info": compound_info,
            "docking_result": docking_result,
            "qsar_result": qsar_result,
            "llm_summary": llm_summary
        }
