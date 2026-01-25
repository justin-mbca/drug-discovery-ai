"""
Tests for Network Analysis with GNN-based scoring
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.network import (
    build_disease_network,
    run_gnn_analysis,
    analyze_network_topology,
    identify_hub_genes,
    find_critical_pathways
)


class TestNetworkBuilding:
    """Test disease network building."""
    
    def test_build_simple_network(self):
        """Test building a simple disease network."""
        pathways = ["pathway1", "pathway2"]
        targets = ["gene1", "gene2"]
        
        network = build_disease_network(pathways, targets)
        
        assert network.number_of_nodes() == 4
        assert network.number_of_edges() == 4  # 2 pathways x 2 targets
    
    def test_network_node_types(self):
        """Test that nodes have correct types."""
        pathways = ["pathway1"]
        targets = ["gene1"]
        
        network = build_disease_network(pathways, targets)
        
        for node, data in network.nodes(data=True):
            assert "type" in data
            assert data["type"] in ["pathway", "gene"]
    
    def test_empty_network(self):
        """Test building network with empty inputs."""
        pathways = []
        targets = []
        
        network = build_disease_network(pathways, targets)
        
        assert network.number_of_nodes() == 0
        assert network.number_of_edges() == 0


class TestGNNAnalysis:
    """Test GNN-based network analysis."""
    
    def test_gnn_analysis_basic(self):
        """Test basic GNN analysis."""
        pathways = ["pathway1", "pathway2"]
        targets = ["gene1", "gene2", "gene3"]
        
        network = build_disease_network(pathways, targets)
        insights = run_gnn_analysis(network)
        
        # Should have scores for all gene nodes
        assert len(insights) == 3
        assert all(gene in insights for gene in targets)
        
        # Scores should be between 0 and 1
        assert all(0 <= score <= 1 for score in insights.values())
    
    def test_gnn_analysis_normalization(self):
        """Test that scores are properly normalized."""
        pathways = ["pathway1", "pathway2", "pathway3"]
        targets = ["gene1", "gene2"]
        
        network = build_disease_network(pathways, targets)
        insights = run_gnn_analysis(network)
        
        # At least one score should be close to 1 (max normalized)
        max_score = max(insights.values())
        assert max_score > 0.9
    
    def test_gnn_analysis_empty_network(self):
        """Test GNN analysis on empty network."""
        pathways = []
        targets = []
        
        network = build_disease_network(pathways, targets)
        insights = run_gnn_analysis(network)
        
        assert insights == {}
    
    def test_gnn_analysis_no_genes(self):
        """Test GNN analysis with only pathways."""
        pathways = ["pathway1", "pathway2"]
        targets = []
        
        network = build_disease_network(pathways, targets)
        insights = run_gnn_analysis(network)
        
        assert insights == {}


class TestNetworkTopology:
    """Test network topology analysis."""
    
    def test_topology_analysis(self):
        """Test basic topology analysis."""
        pathways = ["pathway1", "pathway2"]
        targets = ["gene1", "gene2"]
        
        network = build_disease_network(pathways, targets)
        analysis = analyze_network_topology(network)
        
        assert "num_nodes" in analysis
        assert "num_edges" in analysis
        assert "density" in analysis
        assert "is_connected" in analysis
        
        assert analysis["num_nodes"] == 4
        assert analysis["num_edges"] == 4
        assert analysis["is_connected"] == True
    
    def test_clustering_coefficient(self):
        """Test clustering coefficient calculation."""
        pathways = ["pathway1", "pathway2"]
        targets = ["gene1", "gene2"]
        
        network = build_disease_network(pathways, targets)
        analysis = analyze_network_topology(network)
        
        assert "avg_clustering" in analysis
    
    def test_disconnected_network(self):
        """Test analysis of disconnected network."""
        import networkx as nx
        
        # Create disconnected network manually
        network = nx.Graph()
        network.add_node("gene1", type="gene")
        network.add_node("gene2", type="gene")
        # No edges - disconnected
        
        analysis = analyze_network_topology(network)
        
        assert analysis["is_connected"] == False
        assert "num_components" in analysis


class TestHubGeneIdentification:
    """Test hub gene identification."""
    
    def test_identify_hub_genes(self):
        """Test identification of hub genes."""
        pathways = ["pathway1", "pathway2", "pathway3"]
        targets = ["gene1", "gene2", "gene3"]
        
        network = build_disease_network(pathways, targets)
        hubs = identify_hub_genes(network, top_k=2)
        
        assert len(hubs) <= 2
        assert all(isinstance(item, tuple) for item in hubs)
        assert all(len(item) == 2 for item in hubs)
        
        # Check that hubs are sorted by degree
        if len(hubs) == 2:
            assert hubs[0][1] >= hubs[1][1]
    
    def test_hub_genes_all(self):
        """Test getting all hub genes."""
        pathways = ["pathway1"]
        targets = ["gene1", "gene2"]
        
        network = build_disease_network(pathways, targets)
        hubs = identify_hub_genes(network, top_k=10)
        
        # Should return all genes
        assert len(hubs) == 2


class TestCriticalPathways:
    """Test critical pathway identification."""
    
    def test_find_critical_pathways(self):
        """Test finding critical pathways."""
        pathways = ["pathway1", "pathway2"]
        targets = ["gene1", "gene2"]
        
        network = build_disease_network(pathways, targets)
        critical = find_critical_pathways(network, targets)
        
        # All pathways should be critical (connected to targets)
        assert len(critical) == 2
    
    def test_pathway_prioritization(self):
        """Test that pathways are prioritized by connections."""
        import networkx as nx
        
        # Create custom network with differential connectivity
        network = nx.Graph()
        network.add_node("pathway1", type="pathway")
        network.add_node("pathway2", type="pathway")
        network.add_node("gene1", type="gene")
        network.add_node("gene2", type="gene")
        network.add_node("gene3", type="gene")
        
        # pathway1 connects to 2 genes
        network.add_edge("pathway1", "gene1")
        network.add_edge("pathway1", "gene2")
        
        # pathway2 connects to 1 gene
        network.add_edge("pathway2", "gene3")
        
        critical = find_critical_pathways(network, ["gene1", "gene2", "gene3"])
        
        # pathway1 should be first (more connections)
        assert critical[0] == "pathway1"


# Integration test
def test_complete_network_workflow():
    """Test complete network analysis workflow."""
    print("\nTesting Complete Network Analysis Workflow")
    print("=" * 60)
    
    # Build network
    pathways = ["Alzheimer_pathway", "Neurodegeneration_pathway", "Apoptosis_pathway"]
    targets = ["APP", "BACE1", "MAPT", "PSEN1"]
    
    print(f"\nBuilding network with {len(pathways)} pathways and {len(targets)} targets...")
    network = build_disease_network(pathways, targets)
    
    print(f"Network created: {network.number_of_nodes()} nodes, {network.number_of_edges()} edges")
    
    # Run GNN analysis
    print("\nRunning GNN-based analysis...")
    insights = run_gnn_analysis(network)
    
    print("\nGene Importance Scores:")
    for gene, score in sorted(insights.items(), key=lambda x: x[1], reverse=True):
        print(f"  {gene}: {score:.3f}")
    
    # Topology analysis
    print("\nNetwork Topology:")
    topology = analyze_network_topology(network)
    for key, value in topology.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")
    
    # Hub genes
    print("\nHub Genes:")
    hubs = identify_hub_genes(network, top_k=3)
    for gene, degree in hubs:
        print(f"  {gene}: degree={degree}")
    
    # Critical pathways
    print("\nCritical Pathways:")
    critical = find_critical_pathways(network, targets)
    for pathway in critical:
        print(f"  {pathway}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("Running Network Analysis tests...")
    print("=" * 60)
    
    # Run integration test
    test_complete_network_workflow()
    
    print("\nTests completed! Run 'pytest test_network_analysis.py' for detailed results.")
