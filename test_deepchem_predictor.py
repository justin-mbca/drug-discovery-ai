"""
Tests for DeepChem Molecular Property Predictor
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.deepchem_predictor import DeepChemPredictor


class TestDeepChemPredictor:
    """Test DeepChem-based predictor."""
    
    def test_predictor_creation(self):
        """Test predictor can be created."""
        predictor = DeepChemPredictor()
        assert predictor is not None
    
    def test_predict_solubility(self):
        """Test solubility prediction."""
        predictor = DeepChemPredictor()
        
        if not predictor.available:
            pytest.skip("DeepChem not available")
        
        smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
        result = predictor.predict_solubility(smiles)
        
        assert "error" not in result
        assert "estimated_logS" in result
        assert "solubility_class" in result
        assert isinstance(result["estimated_logS"], float)
    
    def test_predict_toxicity(self):
        """Test toxicity prediction."""
        predictor = DeepChemPredictor()
        
        if not predictor.available:
            pytest.skip("DeepChem not available")
        
        smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
        result = predictor.predict_toxicity(smiles)
        
        assert "error" not in result
        assert "toxicity_risk_score" in result
        assert "toxicity_risk_class" in result
        assert 0 <= result["toxicity_risk_score"] <= 1
    
    def test_predict_admet(self):
        """Test ADMET properties prediction."""
        predictor = DeepChemPredictor()
        
        if not predictor.available:
            pytest.skip("DeepChem not available")
        
        smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
        result = predictor.predict_admet_properties(smiles)
        
        assert "error" not in result
        assert "molecular_weight" in result
        assert "logp" in result
        assert "lipinski_rule_of_5" in result
        assert isinstance(result["lipinski_rule_of_5"], bool)
    
    def test_predict_binding_affinity(self):
        """Test binding affinity prediction."""
        predictor = DeepChemPredictor()
        
        if not predictor.available:
            pytest.skip("DeepChem not available")
        
        smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
        result = predictor.predict_binding_affinity(smiles, "BACE1")
        
        assert "error" not in result
        assert "estimated_binding_score" in result
        assert "target" in result
        assert result["target"] == "BACE1"
    
    def test_generate_fingerprint(self):
        """Test molecular fingerprint generation."""
        predictor = DeepChemPredictor()
        
        if not predictor.available:
            pytest.skip("DeepChem not available")
        
        smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
        fp = predictor.generate_molecular_fingerprint(smiles)
        
        if fp is not None:
            assert fp.shape == (1024,)
            assert fp.dtype == 'int32' or fp.dtype == 'uint8'
    
    def test_compare_molecules(self):
        """Test molecular similarity comparison."""
        predictor = DeepChemPredictor()
        
        if not predictor.available:
            pytest.skip("DeepChem not available")
        
        smiles1 = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
        smiles2 = "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"  # Ibuprofen
        
        result = predictor.compare_molecules(smiles1, smiles2)
        
        assert "error" not in result
        assert "tanimoto_similarity" in result
        assert "dice_similarity" in result
        assert 0 <= result["tanimoto_similarity"] <= 1
        assert 0 <= result["dice_similarity"] <= 1
    
    def test_invalid_smiles(self):
        """Test handling of invalid SMILES."""
        predictor = DeepChemPredictor()
        
        if not predictor.available:
            pytest.skip("DeepChem not available")
        
        invalid_smiles = "INVALID_SMILES_123"
        result = predictor.predict_solubility(invalid_smiles)
        
        assert "error" in result


class TestRuleBasedAssessments:
    """Test rule-based drug-likeness assessments."""
    
    def test_lipinski_rule(self):
        """Test Lipinski's Rule of Five assessment."""
        predictor = DeepChemPredictor()
        
        if not predictor.available:
            pytest.skip("DeepChem not available")
        
        # Aspirin should pass Lipinski's rule
        smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
        result = predictor.predict_admet_properties(smiles)
        
        assert "lipinski_rule_of_5" in result
        # Aspirin typically passes Lipinski's rule
    
    def test_veber_rules(self):
        """Test Veber's rules assessment."""
        predictor = DeepChemPredictor()
        
        if not predictor.available:
            pytest.skip("DeepChem not available")
        
        smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
        result = predictor.predict_admet_properties(smiles)
        
        assert "veber_rules" in result
        assert isinstance(result["veber_rules"], bool)
    
    def test_bioavailability_score(self):
        """Test bioavailability score calculation."""
        predictor = DeepChemPredictor()
        
        if not predictor.available:
            pytest.skip("DeepChem not available")
        
        smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
        result = predictor.predict_admet_properties(smiles)
        
        assert "bioavailability_score" in result
        assert 0 <= result["bioavailability_score"] <= 1


# Test with sample data
def test_comprehensive_prediction():
    """Test comprehensive property prediction for multiple molecules."""
    predictor = DeepChemPredictor()
    
    if not predictor.available:
        print("DeepChem not available. Skipping comprehensive test.")
        return
    
    test_molecules = {
        "Aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "Caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "Ibuprofen": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
    }
    
    print("\nComprehensive DeepChem Predictions:")
    print("=" * 60)
    
    for name, smiles in test_molecules.items():
        print(f"\n{name}:")
        
        # Solubility
        sol = predictor.predict_solubility(smiles)
        if "error" not in sol:
            print(f"  Solubility (LogS): {sol.get('estimated_logS', 'N/A'):.2f}")
            print(f"  Solubility Class: {sol.get('solubility_class', 'N/A')}")
        
        # Toxicity
        tox = predictor.predict_toxicity(smiles)
        if "error" not in tox:
            print(f"  Toxicity Risk: {tox.get('toxicity_risk_class', 'N/A')}")
        
        # ADMET
        admet = predictor.predict_admet_properties(smiles)
        if "error" not in admet:
            print(f"  Lipinski Pass: {admet.get('lipinski_rule_of_5', 'N/A')}")
            print(f"  Bioavailability Score: {admet.get('bioavailability_score', 0):.2f}")


if __name__ == "__main__":
    print("Running DeepChem Predictor tests...")
    print("=" * 60)
    
    # Run comprehensive test
    test_comprehensive_prediction()
    
    print("\n" + "=" * 60)
    print("Tests completed! Run 'pytest test_deepchem_predictor.py' for detailed results.")
