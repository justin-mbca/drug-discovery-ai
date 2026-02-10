import requests
from crewai.tools.base_tool import BaseTool

class PubChemTool(BaseTool):
    name: str = "PubChem Fetch"
    description: str = "Fetch compound data from PubChem. Returns molecular weight, formula, and IUPAC name."

    def _run(self, compound: str):
        # If input is all digits, treat as CID
        if str(compound).isdigit():
            base_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{compound}/property/MolecularWeight,MolecularFormula,IUPACName/JSON"
        else:
            base_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound}/property/MolecularWeight,MolecularFormula,IUPACName/JSON"
        try:
            response = requests.get(base_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            props = data["PropertyTable"]["Properties"][0]
            return {
                "compound": compound,
                "properties": {
                    "molecular_weight": props.get("MolecularWeight"),
                    "formula": props.get("MolecularFormula"),
                    "iupac_name": props.get("IUPACName")
                },
                "source": "PubChem"
            }
        except (requests.RequestException, KeyError, IndexError) as e:
            return {"error": f"PubChem API error: {e}"}