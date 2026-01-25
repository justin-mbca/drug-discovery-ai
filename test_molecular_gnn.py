"""
Tests for GNN-based Molecular Property Predictor
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.molecular_gnn import (
    smiles_to_graph,
    MolecularGNN,
    MolecularPropertyPredictor,
    train_gnn_model
)


class TestSMILESToGraph:
    """Test SMILES to graph conversion."""
    
    def test_valid_smiles(self):
        """Test conversion of valid SMILES strings."""
        # Aspirin
        smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
        graph = smiles_to_graph(smiles)
        
        assert graph is not None
        assert graph.num_nodes > 0
        assert graph.num_edges >= 0
        assert graph.x.shape[1] == 9  # 9 atom features
    
    def test_invalid_smiles(self):
        """Test handling of invalid SMILES strings."""
        invalid_smiles = "INVALID_SMILES_123"
        graph = smiles_to_graph(invalid_smiles)
        
        assert graph is None
    
    def test_simple_molecule(self):
        """Test simple molecule conversion."""
        # Methane
        smiles = "C"
        graph = smiles_to_graph(smiles)
        
        assert graph is not None
        assert graph.num_nodes == 1
        assert graph.num_edges == 0  # Single atom, no bonds
    
    def test_multiple_molecules(self):
        """Test conversion of multiple SMILES strings."""
        test_smiles = [
            "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
            "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
            "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
        ]
        
        for smiles in test_smiles:
            graph = smiles_to_graph(smiles)
            assert graph is not None
            assert graph.num_nodes > 0


class TestMolecularGNN:
    """Test GNN model architecture."""
    
    def test_model_creation(self):
        """Test GNN model can be created."""
        model = MolecularGNN(num_node_features=9, hidden_channels=64, num_classes=1)
        assert model is not None
    
    def test_model_forward_pass(self):
        """Test forward pass through the model."""
        import torch
        
        model = MolecularGNN(num_node_features=9, hidden_channels=64, num_classes=1)
        model.eval()
        
        # Create dummy graph data
        smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
        graph = smiles_to_graph(smiles)
        
        assert graph is not None
        
        with torch.no_grad():
            batch = torch.zeros(graph.num_nodes, dtype=torch.long)
            output = model(graph.x, graph.edge_index, batch)
            
            assert output.shape == (1, 1)  # One prediction
            assert not torch.isnan(output).any()


class TestMolecularPropertyPredictor:
    """Test molecular property predictor."""
    
    def test_predictor_creation(self):
        """Test predictor can be created."""
        predictor = MolecularPropertyPredictor()
        assert predictor is not None
    
    def test_predict_property(self):
        """Test property prediction for a single molecule."""
        predictor = MolecularPropertyPredictor()
        smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
        
        props = predictor.predict_property(smiles)
        
        assert "gnn_score" in props
        assert "molecular_weight" in props
        assert "logp" in props
        assert "lipinski_pass" in props
        assert isinstance(props["molecular_weight"], float)
        assert isinstance(props["lipinski_pass"], bool)
    
    def test_predict_invalid_smiles(self):
        """Test prediction with invalid SMILES."""
        predictor = MolecularPropertyPredictor()
        smiles = "INVALID_SMILES"
        
        props = predictor.predict_property(smiles)
        
        assert "error" in props
    
    def test_predict_batch(self):
        """Test batch prediction."""
        predictor = MolecularPropertyPredictor()
        test_smiles = [
            "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
            "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
        ]
        
        results = predictor.predict_batch(test_smiles)
        
        assert len(results) == 2
        for result in results:
            if "error" not in result:
                assert "gnn_score" in result
                assert "molecular_weight" in result
    
    def test_rank_molecules(self):
        """Test molecule ranking."""
        predictor = MolecularPropertyPredictor()
        test_smiles = [
            "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
            "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
            "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
        ]
        
        ranked = predictor.rank_molecules(test_smiles, criteria="molecular_weight")
        
        assert len(ranked) == 3
        assert all(isinstance(item, tuple) for item in ranked)
        assert all(len(item) == 2 for item in ranked)
        
        # Check that results are sorted
        scores = [score for _, score in ranked]
        assert scores == sorted(scores, reverse=True)


class TestTrainGNN:
    """Test GNN training functionality."""
    
    def test_train_gnn_model(self):
        """Test GNN model training."""
        # Small training set
        train_smiles = [
            "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
            "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
        ]
        train_labels = [0.5, 0.7]
        
        model = train_gnn_model(
            train_smiles,
            train_labels,
            epochs=5,  # Small number for testing
            lr=0.01
        )
        
        assert model is not None


# Test with sample data
def test_end_to_end_workflow():
    """Test complete workflow from SMILES to prediction."""
    # Initialize predictor
    predictor = MolecularPropertyPredictor()
    
    # Test molecules
    test_molecules = {
        "Aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "Caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    }
    
    # Predict properties
    for name, smiles in test_molecules.items():
        props = predictor.predict_property(smiles)
        
        assert "error" not in props
        assert "gnn_score" in props
        assert "molecular_weight" in props
        assert props["molecular_weight"] > 0
        
        print(f"\n{name}:")
        print(f"  Molecular Weight: {props['molecular_weight']:.2f}")
        print(f"  LogP: {props['logp']:.2f}")
        print(f"  Lipinski Pass: {props['lipinski_pass']}")


if __name__ == "__main__":
    print("Running GNN Molecular Property Predictor tests...")
    print("=" * 60)
    
    # Run individual test functions
    test_end_to_end_workflow()
    
    print("\n" + "=" * 60)
    print("Tests completed! Run 'pytest test_molecular_gnn.py' for detailed results.")
