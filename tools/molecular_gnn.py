"""
Molecular Property Predictor using Graph Neural Networks (GNN)
Implements geometric deep learning for molecular property prediction
"""

import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.data import Data, Batch
from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MolecularGNN(torch.nn.Module):
    """
    Graph Neural Network for molecular property prediction.
    Uses Graph Convolutional Networks (GCN) to learn from molecular graphs.
    """
    
    def __init__(self, num_node_features: int = 9, hidden_channels: int = 64, num_classes: int = 1):
        super(MolecularGNN, self).__init__()
        self.conv1 = GCNConv(num_node_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels)
        self.lin = torch.nn.Linear(hidden_channels, num_classes)
        
    def forward(self, x, edge_index, batch):
        # First GCN layer
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.2, training=self.training)
        
        # Second GCN layer
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.2, training=self.training)
        
        # Third GCN layer
        x = self.conv3(x, edge_index)
        x = F.relu(x)
        
        # Global pooling (mean)
        x = global_mean_pool(x, batch)
        
        # Final linear layer
        x = self.lin(x)
        
        return x


def smiles_to_graph(smiles: str) -> Optional[Data]:
    """
    Convert SMILES string to PyTorch Geometric graph representation.
    
    Args:
        smiles: SMILES string representing a molecule
        
    Returns:
        PyTorch Geometric Data object or None if conversion fails
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            logger.warning(f"Failed to parse SMILES: {smiles}")
            return None
        
        # Get atom features
        atom_features = []
        for atom in mol.GetAtoms():
            # Basic atomic features
            features = [
                atom.GetAtomicNum(),  # Atomic number
                atom.GetDegree(),  # Degree
                atom.GetFormalCharge(),  # Formal charge
                atom.GetHybridization().real,  # Hybridization
                atom.GetIsAromatic(),  # Is aromatic
                atom.GetTotalNumHs(),  # Total hydrogens
                atom.GetNumRadicalElectrons(),  # Radical electrons
                atom.IsInRing(),  # In ring
                atom.GetChiralTag().real  # Chirality
            ]
            atom_features.append(features)
        
        x = torch.tensor(atom_features, dtype=torch.float)
        
        # Get edge indices (bonds)
        edge_indices = []
        for bond in mol.GetBonds():
            i = bond.GetBeginAtomIdx()
            j = bond.GetEndAtomIdx()
            edge_indices.append([i, j])
            edge_indices.append([j, i])  # Add reverse edge for undirected graph
        
        if len(edge_indices) == 0:
            # Single atom molecule
            edge_index = torch.empty((2, 0), dtype=torch.long)
        else:
            edge_index = torch.tensor(edge_indices, dtype=torch.long).t().contiguous()
        
        # Create PyTorch Geometric Data object
        data = Data(x=x, edge_index=edge_index)
        
        return data
        
    except Exception as e:
        logger.error(f"Error converting SMILES {smiles} to graph: {e}")
        return None


class MolecularPropertyPredictor:
    """
    High-level interface for molecular property prediction using GNN.
    Predicts various molecular properties like solubility, toxicity, and binding affinity.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the molecular property predictor.
        
        Args:
            model_path: Path to pre-trained model weights (optional)
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = MolecularGNN(num_node_features=9, hidden_channels=64, num_classes=1)
        self.model.to(self.device)
        
        if model_path:
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                print(f"Loaded pre-trained model from {model_path}")
            except Exception as e:
                print(f"Warning: Could not load model from {model_path}: {e}")
                print("Using randomly initialized model")
        
        self.model.eval()
    
    def predict_property(self, smiles: str) -> Dict[str, float]:
        """
        Predict molecular properties for a given SMILES string.
        
        Args:
            smiles: SMILES string of the molecule
            
        Returns:
            Dictionary containing predicted properties
        """
        graph = smiles_to_graph(smiles)
        if graph is None:
            return {"error": "Invalid SMILES string"}
        
        # Move to device
        graph = graph.to(self.device)
        
        # Predict
        with torch.no_grad():
            batch = torch.zeros(graph.num_nodes, dtype=torch.long, device=self.device)
            prediction = self.model(graph.x, graph.edge_index, batch)
            score = prediction.item()
        
        # Calculate additional molecular descriptors using RDKit
        mol = Chem.MolFromSmiles(smiles)
        properties = {
            "gnn_score": score,
            "molecular_weight": Descriptors.MolWt(mol),
            "logp": Descriptors.MolLogP(mol),
            "num_h_acceptors": Descriptors.NumHAcceptors(mol),
            "num_h_donors": Descriptors.NumHDonors(mol),
            "tpsa": Descriptors.TPSA(mol),
            "num_rotatable_bonds": Descriptors.NumRotatableBonds(mol),
            "num_aromatic_rings": Descriptors.NumAromaticRings(mol),
        }
        
        # Add Lipinski's Rule of Five assessment
        properties["lipinski_pass"] = (
            properties["molecular_weight"] <= 500 and
            properties["logp"] <= 5 and
            properties["num_h_donors"] <= 5 and
            properties["num_h_acceptors"] <= 10
        )
        
        return properties
    
    def predict_batch(self, smiles_list: List[str]) -> List[Dict[str, float]]:
        """
        Predict properties for a batch of molecules.
        
        Args:
            smiles_list: List of SMILES strings
            
        Returns:
            List of property dictionaries
        """
        results = []
        for smiles in smiles_list:
            results.append(self.predict_property(smiles))
        return results
    
    def rank_molecules(self, smiles_list: List[str], criteria: str = "gnn_score") -> List[Tuple[str, float]]:
        """
        Rank molecules based on predicted properties.
        
        Args:
            smiles_list: List of SMILES strings
            criteria: Property to rank by (default: gnn_score)
            
        Returns:
            List of (smiles, score) tuples, sorted by score
        """
        results = self.predict_batch(smiles_list)
        ranked = []
        for smiles, props in zip(smiles_list, results):
            if "error" not in props and criteria in props:
                ranked.append((smiles, props[criteria]))
        
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked


def train_gnn_model(
    train_smiles: List[str],
    train_labels: List[float],
    epochs: int = 100,
    lr: float = 0.01,
    save_path: Optional[str] = None
) -> MolecularGNN:
    """
    Train a GNN model on molecular data.
    
    Args:
        train_smiles: List of SMILES strings for training
        train_labels: List of target labels (e.g., binding affinity)
        epochs: Number of training epochs
        lr: Learning rate
        save_path: Path to save trained model (optional)
        
    Returns:
        Trained MolecularGNN model
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = MolecularGNN(num_node_features=9, hidden_channels=64, num_classes=1)
    model.to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = torch.nn.MSELoss()
    
    # Convert SMILES to graphs
    train_data = []
    train_targets = []
    for smiles, label in zip(train_smiles, train_labels):
        graph = smiles_to_graph(smiles)
        if graph is not None:
            train_data.append(graph)
            train_targets.append(label)
    
    print(f"Training on {len(train_data)} molecules for {epochs} epochs")
    
    # Training loop
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for graph, target in zip(train_data, train_targets):
            graph = graph.to(device)
            target_tensor = torch.tensor([target], dtype=torch.float, device=device)
            
            optimizer.zero_grad()
            batch = torch.zeros(graph.num_nodes, dtype=torch.long, device=device)
            out = model(graph.x, graph.edge_index, batch)
            loss = criterion(out, target_tensor)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            avg_loss = total_loss / len(train_data)
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
    
    # Save model if path provided
    if save_path:
        torch.save(model.state_dict(), save_path)
        print(f"Model saved to {save_path}")
    
    return model


# Example usage and testing
if __name__ == "__main__":
    print("Testing Molecular Property Predictor with GNN")
    print("=" * 60)
    
    # Test SMILES strings
    test_smiles = [
        "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
    ]
    
    print("\n1. Converting SMILES to graphs:")
    for smiles in test_smiles:
        graph = smiles_to_graph(smiles)
        if graph:
            print(f"  {smiles[:30]}... -> Graph with {graph.num_nodes} nodes, {graph.num_edges} edges")
    
    print("\n2. Predicting molecular properties:")
    predictor = MolecularPropertyPredictor()
    
    for smiles in test_smiles:
        print(f"\nSMILES: {smiles}")
        props = predictor.predict_property(smiles)
        for key, value in props.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")
    
    print("\n3. Ranking molecules by GNN score:")
    ranked = predictor.rank_molecules(test_smiles)
    for i, (smiles, score) in enumerate(ranked, 1):
        print(f"  {i}. Score: {score:.3f} - {smiles[:40]}...")
    
    print("\n" + "=" * 60)
    print("GNN Molecular Property Predictor test complete!")
