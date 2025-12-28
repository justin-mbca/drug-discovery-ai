"""
Enhanced protein structure analysis tools for working with PDB files.
Includes parsing, analysis, and structural bioinformatics features.
"""

import os
from typing import Dict, List, Optional, Tuple
import numpy as np

try:
    from Bio.PDB import PDBParser, PDBIO, Select, Superimposer
    from Bio.PDB.DSSP import DSSP
    from Bio.PDB.Polypeptide import PPBuilder
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False
    print("Warning: Biopython not available. Install with: pip install biopython")


class PDBAnalyzer:
    """
    Analyze protein structures from PDB files.
    Provides structural analysis, quality metrics, and binding site identification.
    """
    
    def __init__(self):
        """Initialize PDB analyzer."""
        if not BIOPYTHON_AVAILABLE:
            print("Biopython is not installed. PDB analysis features will be limited.")
            self.available = False
            return
        
        self.available = True
        self.parser = PDBParser(QUIET=True)
    
    def parse_pdb(self, pdb_file: str) -> Optional[any]:
        """
        Parse a PDB file and return structure object.
        
        Args:
            pdb_file: Path to PDB file
            
        Returns:
            Biopython Structure object or None
        """
        if not self.available:
            return None
        
        try:
            structure = self.parser.get_structure("protein", pdb_file)
            return structure
        except Exception as e:
            print(f"Error parsing PDB file {pdb_file}: {e}")
            return None
    
    def get_structure_info(self, pdb_file: str) -> Dict[str, any]:
        """
        Get basic information about a protein structure.
        
        Args:
            pdb_file: Path to PDB file
            
        Returns:
            Dictionary with structure information
        """
        if not self.available:
            return {"error": "Biopython not available"}
        
        structure = self.parse_pdb(pdb_file)
        if structure is None:
            return {"error": "Failed to parse PDB file"}
        
        try:
            info = {
                "structure_id": structure.id,
                "num_models": len(structure),
                "num_chains": 0,
                "num_residues": 0,
                "num_atoms": 0,
                "chains": []
            }
            
            for model in structure:
                for chain in model:
                    info["num_chains"] += 1
                    chain_info = {
                        "chain_id": chain.id,
                        "num_residues": len(chain),
                        "num_atoms": len(list(chain.get_atoms()))
                    }
                    info["chains"].append(chain_info)
                    info["num_residues"] += chain_info["num_residues"]
                    info["num_atoms"] += chain_info["num_atoms"]
            
            return info
            
        except Exception as e:
            return {"error": f"Structure analysis failed: {str(e)}"}
    
    def get_sequence(self, pdb_file: str, chain_id: Optional[str] = None) -> Dict[str, str]:
        """
        Extract amino acid sequence from PDB file.
        
        Args:
            pdb_file: Path to PDB file
            chain_id: Specific chain ID (optional, uses first chain if not specified)
            
        Returns:
            Dictionary with sequence information
        """
        if not BIOPYTHON_AVAILABLE:
            return {"error": "Biopython not available"}
        
        structure = self.parse_pdb(pdb_file)
        if structure is None:
            return {"error": "Failed to parse PDB file"}
        
        try:
            ppb = PPBuilder()
            sequences = {}
            
            for model in structure:
                for chain in model:
                    if chain_id and chain.id != chain_id:
                        continue
                    
                    peptides = ppb.build_peptides(chain)
                    seq = "".join([str(pp.get_sequence()) for pp in peptides])
                    sequences[chain.id] = seq
            
            return sequences
            
        except Exception as e:
            return {"error": f"Sequence extraction failed: {str(e)}"}
    
    def calculate_center_of_mass(self, pdb_file: str) -> Dict[str, any]:
        """
        Calculate center of mass for the protein structure.
        
        Args:
            pdb_file: Path to PDB file
            
        Returns:
            Dictionary with center of mass coordinates
        """
        if not self.available:
            return {"error": "Biopython not available"}
        
        structure = self.parse_pdb(pdb_file)
        if structure is None:
            return {"error": "Failed to parse PDB file"}
        
        try:
            atoms = list(structure.get_atoms())
            coords = np.array([atom.coord for atom in atoms])
            center = np.mean(coords, axis=0)
            
            return {
                "center_of_mass": {
                    "x": float(center[0]),
                    "y": float(center[1]),
                    "z": float(center[2])
                },
                "num_atoms": len(atoms)
            }
            
        except Exception as e:
            return {"error": f"Center of mass calculation failed: {str(e)}"}
    
    def find_binding_site(self, pdb_file: str, ligand_name: Optional[str] = None) -> Dict[str, any]:
        """
        Identify potential binding sites or ligands in the structure.
        
        Args:
            pdb_file: Path to PDB file
            ligand_name: Optional specific ligand name to search for
            
        Returns:
            Dictionary with binding site information
        """
        if not self.available:
            return {"error": "Biopython not available"}
        
        structure = self.parse_pdb(pdb_file)
        if structure is None:
            return {"error": "Failed to parse PDB file"}
        
        try:
            hetero_residues = []
            
            for model in structure:
                for chain in model:
                    for residue in chain:
                        # HETATM residues (non-standard, often ligands)
                        if residue.id[0] != " ":
                            het_id = residue.id[0]
                            res_name = residue.resname.strip()
                            
                            if ligand_name and res_name != ligand_name:
                                continue
                            
                            # Calculate center of hetero residue
                            atoms = list(residue.get_atoms())
                            if atoms:
                                coords = np.array([atom.coord for atom in atoms])
                                center = np.mean(coords, axis=0)
                                
                                hetero_residues.append({
                                    "chain_id": chain.id,
                                    "residue_name": res_name,
                                    "residue_id": residue.id[1],
                                    "num_atoms": len(atoms),
                                    "center": {
                                        "x": float(center[0]),
                                        "y": float(center[1]),
                                        "z": float(center[2])
                                    }
                                })
            
            return {
                "num_ligands": len(hetero_residues),
                "ligands": hetero_residues
            }
            
        except Exception as e:
            return {"error": f"Binding site analysis failed: {str(e)}"}
    
    def calculate_residue_distances(self, pdb_file: str, residue1_id: int, residue2_id: int, 
                                   chain_id: str = "A") -> Dict[str, float]:
        """
        Calculate distance between two residues.
        
        Args:
            pdb_file: Path to PDB file
            residue1_id: First residue ID
            residue2_id: Second residue ID
            chain_id: Chain ID (default: "A")
            
        Returns:
            Dictionary with distance information
        """
        if not self.available:
            return {"error": "Biopython not available"}
        
        structure = self.parse_pdb(pdb_file)
        if structure is None:
            return {"error": "Failed to parse PDB file"}
        
        try:
            model = structure[0]
            chain = model[chain_id]
            
            res1 = chain[(" ", residue1_id, " ")]
            res2 = chain[(" ", residue2_id, " ")]
            
            # Calculate CA-CA distance (most common metric)
            ca1 = res1["CA"].coord
            ca2 = res2["CA"].coord
            ca_distance = np.linalg.norm(ca1 - ca2)
            
            # Calculate minimum distance between any atoms
            min_distance = float('inf')
            for atom1 in res1:
                for atom2 in res2:
                    dist = np.linalg.norm(atom1.coord - atom2.coord)
                    min_distance = min(min_distance, dist)
            
            return {
                "ca_distance": float(ca_distance),
                "min_atom_distance": float(min_distance),
                "residue1": res1.resname,
                "residue2": res2.resname
            }
            
        except Exception as e:
            return {"error": f"Distance calculation failed: {str(e)}"}
    
    def get_secondary_structure(self, pdb_file: str) -> Dict[str, any]:
        """
        Analyze secondary structure using DSSP (if available).
        
        Args:
            pdb_file: Path to PDB file
            
        Returns:
            Dictionary with secondary structure information
        """
        if not self.available:
            return {"error": "Biopython not available"}
        
        structure = self.parse_pdb(pdb_file)
        if structure is None:
            return {"error": "Failed to parse PDB file"}
        
        # Note: DSSP requires external DSSP program to be installed
        # This is a simplified version without DSSP
        return {
            "note": "Secondary structure analysis requires DSSP program",
            "suggestion": "Install DSSP for detailed secondary structure analysis"
        }
    
    def get_quality_metrics(self, pdb_file: str) -> Dict[str, any]:
        """
        Calculate quality metrics for the structure (simplified).
        
        Args:
            pdb_file: Path to PDB file
            
        Returns:
            Dictionary with quality metrics
        """
        if not self.available:
            return {"error": "Biopython not available"}
        
        structure = self.parse_pdb(pdb_file)
        if structure is None:
            return {"error": "Failed to parse PDB file"}
        
        try:
            atoms = list(structure.get_atoms())
            
            # Check for missing atoms (incomplete residues)
            incomplete_residues = 0
            total_residues = 0
            
            for model in structure:
                for chain in model:
                    for residue in chain:
                        if residue.id[0] == " ":  # Standard amino acid
                            total_residues += 1
                            # Check for backbone atoms
                            has_n = "N" in residue
                            has_ca = "CA" in residue
                            has_c = "C" in residue
                            has_o = "O" in residue
                            
                            if not (has_n and has_ca and has_c and has_o):
                                incomplete_residues += 1
            
            completeness = 1.0 - (incomplete_residues / total_residues) if total_residues > 0 else 0.0
            
            return {
                "total_atoms": len(atoms),
                "total_residues": total_residues,
                "incomplete_residues": incomplete_residues,
                "structure_completeness": float(completeness),
                "quality_assessment": "good" if completeness > 0.95 else "moderate" if completeness > 0.85 else "poor"
            }
            
        except Exception as e:
            return {"error": f"Quality assessment failed: {str(e)}"}


# Enhanced AlphaFold tool with PDB analysis
class EnhancedAlphaFoldTool:
    """
    Enhanced AlphaFold tool with comprehensive PDB file analysis.
    """
    
    def __init__(self, structure_dir="data/alphafold_structures"):
        self.structure_dir = structure_dir
        self.analyzer = PDBAnalyzer()
        os.makedirs(structure_dir, exist_ok=True)
    
    def predict(self, uniprot_id: str) -> str:
        """
        Get AlphaFold structure for a UniProt ID.
        Downloads if not available locally.
        
        Args:
            uniprot_id: UniProt identifier
            
        Returns:
            PDB file content as string
        """
        filename = f"{uniprot_id}.pdb"
        filepath = os.path.join(self.structure_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        
        # Download from AlphaFold database
        import requests
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
    
    def analyze_structure(self, uniprot_id: str) -> Dict[str, any]:
        """
        Download and analyze an AlphaFold structure.
        
        Args:
            uniprot_id: UniProt identifier
            
        Returns:
            Dictionary with comprehensive structure analysis
        """
        # Ensure structure is available
        pdb_content = self.predict(uniprot_id)
        if "not found" in pdb_content or "Error" in pdb_content:
            return {"error": pdb_content}
        
        filepath = os.path.join(self.structure_dir, f"{uniprot_id}.pdb")
        
        # Perform analysis
        results = {
            "uniprot_id": uniprot_id,
            "pdb_file": filepath,
            "structure_info": self.analyzer.get_structure_info(filepath),
            "sequence": self.analyzer.get_sequence(filepath),
            "center_of_mass": self.analyzer.calculate_center_of_mass(filepath),
            "binding_sites": self.analyzer.find_binding_site(filepath),
            "quality_metrics": self.analyzer.get_quality_metrics(filepath)
        }
        
        return results


# Example usage and testing
if __name__ == "__main__":
    print("Testing PDB Structure Analysis Tools")
    print("=" * 60)
    
    analyzer = PDBAnalyzer()
    
    if not analyzer.available:
        print("Biopython is not installed. PDB analysis features are limited.")
        print("Install with: pip install biopython")
    else:
        print("PDB analyzer initialized successfully!")
        print("\nTo test PDB analysis:")
        print("1. Download a PDB file (e.g., from https://www.rcsb.org/)")
        print("2. Run: analyzer.get_structure_info('path/to/file.pdb')")
        print("3. Or use EnhancedAlphaFoldTool to download and analyze AlphaFold structures")
        
        print("\nExample AlphaFold usage:")
        print("  tool = EnhancedAlphaFoldTool()")
        print("  results = tool.analyze_structure('P12345')  # Replace with UniProt ID")
    
    print("\n" + "=" * 60)
    print("PDB analysis tools ready!")
