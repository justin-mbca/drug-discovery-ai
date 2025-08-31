# tools/alphafold.py

import os

class AlphaFoldTool:
    def __init__(self, structure_dir="data/alphafold_structures"):
        self.structure_dir = structure_dir

    def predict(self, uniprot_id):
        """
        Returns the contents of a precomputed AlphaFold PDB file for the given UniProt ID,
        or a message if not found.
        """
        filename = f"{uniprot_id}.pdb"
        filepath = os.path.join(self.structure_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return f"No precomputed AlphaFold structure found for {uniprot_id}. Download from https://alphafold.ebi.ac.uk/entry/{uniprot_id} and place in {self.structure_dir}/ as {filename}."
