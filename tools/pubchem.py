

# Add PubChemTool class for agent compatibility

import requests

class PubChemTool:
    def lookup(self, compound):
        """
        Look up compound information from PubChem using the PUG REST API.
        Supports both compound names and numeric CIDs.
        Returns a dictionary with compound info or an error message.
        """
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

def fetch_compound_data(compound: str) -> dict:
    """
    Placeholder function for fetching compound data from PubChem or similar service.
    Returns mock data for development/testing.
    """
    return {
        "compound": compound,
        "properties": {
            "molecular_weight": 123.45,
            "formula": "C6H12O6",
            "iupac_name": "glucose"
        },
        "source": "mock"
    }
