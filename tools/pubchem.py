

# Add PubChemTool class for agent compatibility
class PubChemTool:
    def lookup(self, compound):
        # Stub: Replace with real PubChem API call or use fetch_compound_data
        return f"Mock PubChem info for {compound}"

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
