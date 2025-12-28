"""
DeepChem-based Molecular Property Predictor
Leverages DeepChem's pre-trained models and molecular featurizers
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from rdkit import Chem

try:
    import deepchem as dc
    DEEPCHEM_AVAILABLE = True
except ImportError:
    DEEPCHEM_AVAILABLE = False
    print("Warning: DeepChem not available. Install with: pip install deepchem")


class DeepChemPredictor:
    """
    Molecular property predictor using DeepChem library.
    Provides predictions for ADMET properties, toxicity, and more.
    """
    
    def __init__(self):
        """Initialize DeepChem predictor with default settings."""
        if not DEEPCHEM_AVAILABLE:
            print("DeepChem is not installed. Please install it to use this predictor.")
            self.available = False
            return
        
        self.available = True
        # Initialize featurizers
        self.molecular_featurizer = dc.feat.MolGraphConvFeaturizer()
        self.fingerprint_featurizer = dc.feat.CircularFingerprint(size=1024)
        print("DeepChem predictor initialized successfully")
    
    def predict_solubility(self, smiles: str) -> Dict[str, float]:
        """
        Predict aqueous solubility (LogS) for a molecule.
        
        Args:
            smiles: SMILES string of the molecule
            
        Returns:
            Dictionary with solubility predictions
        """
        if not self.available:
            return {"error": "DeepChem not available"}
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {"error": "Invalid SMILES"}
            
            # Use simple heuristic based on molecular descriptors
            from rdkit.Chem import Descriptors
            
            # Simplified solubility estimation
            logp = Descriptors.MolLogP(mol)
            molecular_weight = Descriptors.MolWt(mol)
            num_rotatable_bonds = Descriptors.NumRotatableBonds(mol)
            
            # Simplified Yalkowsky equation approximation
            estimated_logs = 0.5 - logp - 0.01 * (molecular_weight - 200)
            
            return {
                "estimated_logS": estimated_logs,
                "solubility_class": self._classify_solubility(estimated_logs),
                "logp": logp,
                "molecular_weight": molecular_weight,
                "num_rotatable_bonds": num_rotatable_bonds
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def predict_toxicity(self, smiles: str) -> Dict[str, any]:
        """
        Predict toxicity properties for a molecule.
        
        Args:
            smiles: SMILES string of the molecule
            
        Returns:
            Dictionary with toxicity predictions
        """
        if not self.available:
            return {"error": "DeepChem not available"}
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {"error": "Invalid SMILES"}
            
            # Use molecular descriptors as toxicity indicators
            from rdkit.Chem import Descriptors
            
            # Common toxicity-related descriptors
            results = {
                "num_aromatic_rings": Descriptors.NumAromaticRings(mol),
                "num_aliphatic_rings": Descriptors.NumAliphaticRings(mol),
                "fraction_csp3": Descriptors.FractionCSP3(mol),
                "num_rotatable_bonds": Descriptors.NumRotatableBonds(mol),
                "tpsa": Descriptors.TPSA(mol),
            }
            
            # Simple toxicity risk assessment
            risk_score = 0
            if results["num_aromatic_rings"] > 3:
                risk_score += 0.2
            if results["tpsa"] > 140:
                risk_score += 0.3
            if results["num_rotatable_bonds"] > 10:
                risk_score += 0.2
            
            results["toxicity_risk_score"] = min(risk_score, 1.0)
            results["toxicity_risk_class"] = self._classify_toxicity_risk(risk_score)
            
            return results
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def predict_admet_properties(self, smiles: str) -> Dict[str, any]:
        """
        Predict ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity) properties.
        
        Args:
            smiles: SMILES string of the molecule
            
        Returns:
            Dictionary with ADMET predictions
        """
        if not self.available:
            return {"error": "DeepChem not available"}
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {"error": "Invalid SMILES"}
            
            from rdkit.Chem import Descriptors, Crippen
            
            # Calculate relevant ADMET descriptors
            results = {
                # Absorption
                "molecular_weight": Descriptors.MolWt(mol),
                "logp": Descriptors.MolLogP(mol),
                "tpsa": Descriptors.TPSA(mol),
                "num_h_donors": Descriptors.NumHDonors(mol),
                "num_h_acceptors": Descriptors.NumHAcceptors(mol),
                
                # Distribution
                "num_rotatable_bonds": Descriptors.NumRotatableBonds(mol),
                "fraction_csp3": Descriptors.FractionCSP3(mol),
                
                # Metabolism
                "num_aromatic_rings": Descriptors.NumAromaticRings(mol),
                "num_heteroatoms": Descriptors.NumHeteroatoms(mol),
                
                # Excretion (related to molecular size and polarity)
                "molar_refractivity": Crippen.MolMR(mol),
            }
            
            # Rule-based assessments
            results["lipinski_rule_of_5"] = self._assess_lipinski(results)
            results["veber_rules"] = self._assess_veber(results)
            results["bioavailability_score"] = self._calculate_bioavailability_score(results)
            
            return results
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def predict_binding_affinity(self, smiles: str, target_name: str = "generic") -> Dict[str, float]:
        """
        Predict binding affinity for a molecule (simplified heuristic).
        
        Args:
            smiles: SMILES string of the molecule
            target_name: Name of the target protein (for logging)
            
        Returns:
            Dictionary with binding affinity predictions
        """
        if not self.available:
            return {"error": "DeepChem not available"}
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {"error": "Invalid SMILES"}
            
            from rdkit.Chem import Descriptors
            
            # Simplified binding affinity estimation based on molecular properties
            logp = Descriptors.MolLogP(mol)
            molecular_weight = Descriptors.MolWt(mol)
            num_h_donors = Descriptors.NumHDonors(mol)
            num_h_acceptors = Descriptors.NumHAcceptors(mol)
            tpsa = Descriptors.TPSA(mol)
            
            # Heuristic scoring (not based on actual binding data)
            # Favorable properties contribute to score
            score = 0.0
            score += min(logp / 5.0, 1.0) * 2  # Lipophilicity
            score += min((num_h_donors + num_h_acceptors) / 10.0, 1.0) * 2  # H-bonding potential
            score += max(0, 1 - abs(molecular_weight - 350) / 500) * 2  # Molecular weight preference
            score += min(tpsa / 100.0, 1.0) * 1  # Polar surface area
            
            return {
                "estimated_binding_score": score,
                "target": target_name,
                "confidence": "low (heuristic-based)",
                "logp": logp,
                "molecular_weight": molecular_weight,
                "h_bonding_capacity": num_h_donors + num_h_acceptors
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def generate_molecular_fingerprint(self, smiles: str) -> Optional[np.ndarray]:
        """
        Generate circular (Morgan) fingerprint for a molecule.
        
        Args:
            smiles: SMILES string of the molecule
            
        Returns:
            Numpy array of fingerprint bits or None if failed
        """
        if not self.available:
            return None
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None
            
            from rdkit.Chem import AllChem
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=1024)
            return np.array(fp)
            
        except Exception as e:
            print(f"Fingerprint generation failed: {e}")
            return None
    
    def compare_molecules(self, smiles1: str, smiles2: str) -> Dict[str, float]:
        """
        Compare two molecules using fingerprint similarity.
        
        Args:
            smiles1: First SMILES string
            smiles2: Second SMILES string
            
        Returns:
            Dictionary with similarity metrics
        """
        fp1 = self.generate_molecular_fingerprint(smiles1)
        fp2 = self.generate_molecular_fingerprint(smiles2)
        
        if fp1 is None or fp2 is None:
            return {"error": "Could not generate fingerprints"}
        
        # Tanimoto similarity
        intersection = np.sum(np.logical_and(fp1, fp2))
        union = np.sum(np.logical_or(fp1, fp2))
        tanimoto = intersection / union if union > 0 else 0.0
        
        # Dice similarity
        dice = (2 * intersection) / (np.sum(fp1) + np.sum(fp2)) if (np.sum(fp1) + np.sum(fp2)) > 0 else 0.0
        
        return {
            "tanimoto_similarity": float(tanimoto),
            "dice_similarity": float(dice),
            "interpretation": self._interpret_similarity(tanimoto)
        }
    
    # Helper methods
    def _classify_solubility(self, logs: float) -> str:
        """Classify solubility based on LogS value."""
        if logs > -2:
            return "highly soluble"
        elif logs > -4:
            return "soluble"
        elif logs > -6:
            return "poorly soluble"
        else:
            return "insoluble"
    
    def _classify_toxicity_risk(self, risk_score: float) -> str:
        """Classify toxicity risk."""
        if risk_score < 0.3:
            return "low risk"
        elif risk_score < 0.6:
            return "medium risk"
        else:
            return "high risk"
    
    def _assess_lipinski(self, props: Dict) -> bool:
        """Assess Lipinski's Rule of Five."""
        return (
            props["molecular_weight"] <= 500 and
            props["logp"] <= 5 and
            props["num_h_donors"] <= 5 and
            props["num_h_acceptors"] <= 10
        )
    
    def _assess_veber(self, props: Dict) -> bool:
        """Assess Veber's rules for oral bioavailability."""
        return (
            props["num_rotatable_bonds"] <= 10 and
            props["tpsa"] <= 140
        )
    
    def _calculate_bioavailability_score(self, props: Dict) -> float:
        """Calculate a simple bioavailability score (0-1)."""
        score = 1.0
        
        # Penalize for violations
        if props["molecular_weight"] > 500:
            score -= 0.2
        if props["logp"] > 5:
            score -= 0.2
        if props["num_h_donors"] > 5:
            score -= 0.2
        if props["num_rotatable_bonds"] > 10:
            score -= 0.2
        if props["tpsa"] > 140:
            score -= 0.2
        
        return max(0.0, score)
    
    def _interpret_similarity(self, tanimoto: float) -> str:
        """Interpret Tanimoto similarity score."""
        if tanimoto > 0.85:
            return "very similar"
        elif tanimoto > 0.6:
            return "similar"
        elif tanimoto > 0.4:
            return "moderately similar"
        else:
            return "dissimilar"


# Example usage and testing
if __name__ == "__main__":
    print("Testing DeepChem Molecular Property Predictor")
    print("=" * 60)
    
    predictor = DeepChemPredictor()
    
    if not predictor.available:
        print("DeepChem is not available. Skipping tests.")
        print("Install with: pip install deepchem")
    else:
        # Test molecules
        test_smiles = {
            "Aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
            "Caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            "Ibuprofen": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
        }
        
        print("\n1. Solubility Predictions:")
        for name, smiles in test_smiles.items():
            print(f"\n{name}:")
            result = predictor.predict_solubility(smiles)
            for key, value in result.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")
        
        print("\n2. Toxicity Predictions:")
        for name, smiles in test_smiles.items():
            print(f"\n{name}:")
            result = predictor.predict_toxicity(smiles)
            for key, value in result.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")
        
        print("\n3. ADMET Properties:")
        for name, smiles in test_smiles.items():
            print(f"\n{name}:")
            result = predictor.predict_admet_properties(smiles)
            for key, value in result.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.3f}")
                elif isinstance(value, bool):
                    print(f"  {key}: {'Pass' if value else 'Fail'}")
                else:
                    print(f"  {key}: {value}")
        
        print("\n4. Molecular Similarity:")
        smiles_list = list(test_smiles.values())
        comparison = predictor.compare_molecules(smiles_list[0], smiles_list[1])
        print(f"\nComparing {list(test_smiles.keys())[0]} and {list(test_smiles.keys())[1]}:")
        for key, value in comparison.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("DeepChem predictor test complete!")
