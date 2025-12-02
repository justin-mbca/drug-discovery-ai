# tools/alphafold.py


import os
import requests

class AlphaFoldTool:
    def __init__(self, structure_dir="data/alphafold_structures"):
        self.structure_dir = structure_dir

    def predict(self, uniprot_id):
        """
        Returns the contents of a precomputed AlphaFold PDB file for the given UniProt ID.
        If not found locally, attempts to download it automatically from the AlphaFold EBI database.
        """
        filename = f"{uniprot_id}.pdb"
        filepath = os.path.join(self.structure_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        # Try to download automatically
        os.makedirs(self.structure_dir, exist_ok=True)
        pdb_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
        try:
            resp = requests.get(pdb_url, timeout=20)
            if resp.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                with open(filepath, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                return f"AlphaFold structure for {uniprot_id} not found online (status {resp.status_code}). Download manually from https://alphafold.ebi.ac.uk/entry/{uniprot_id} if needed."
        except Exception as e:
            return f"Error downloading AlphaFold structure for {uniprot_id}: {e}"
