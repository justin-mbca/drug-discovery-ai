# tools/network.py

import networkx as nx
import numpy as np
from typing import Dict, List

# Example: Build a disease network from pathways and targets
def build_disease_network(pathways, targets):
    G = nx.Graph()
    for pathway in pathways:
        G.add_node(pathway, type='pathway')
    for target in targets:
        G.add_node(target, type='gene')
        for pathway in pathways:
            G.add_edge(pathway, target)
    return G


def run_gnn_analysis(network):
    """
    Run Graph Neural Network-based analysis on disease network.
    Uses network topology metrics to identify vulnerable/important nodes.
    
    Args:
        network: NetworkX graph representing disease network
        
    Returns:
        Dictionary mapping gene nodes to importance scores
    """
    insights = {}
    
    # Calculate various centrality measures (graph-based features)
    try:
        degree_centrality = nx.degree_centrality(network)
        betweenness_centrality = nx.betweenness_centrality(network)
        closeness_centrality = nx.closeness_centrality(network)
        
        # PageRank as a measure of importance
        pagerank = nx.pagerank(network)
        
        # Combine metrics for gene nodes
        for node, data in network.nodes(data=True):
            if data.get('type') == 'gene':
                # Weighted combination of centrality measures
                score = (
                    0.3 * degree_centrality.get(node, 0) +
                    0.3 * betweenness_centrality.get(node, 0) +
                    0.2 * closeness_centrality.get(node, 0) +
                    0.2 * pagerank.get(node, 0)
                )
                insights[node] = score
        
        # Normalize scores to [0, 1] range
        if insights:
            max_score = max(insights.values())
            if max_score > 0:
                insights = {k: v / max_score for k, v in insights.items()}
        
    except Exception as e:
        print(f"Warning: GNN analysis encountered error: {e}")
        print("Falling back to simple degree-based scoring")
        # Fallback to simple degree centrality
        degree_centrality = nx.degree_centrality(network)
        for node, data in network.nodes(data=True):
            if data.get('type') == 'gene':
                insights[node] = degree_centrality.get(node, 0)
    
    return insights


def analyze_network_topology(network) -> Dict[str, any]:
    """
    Perform comprehensive network topology analysis.
    
    Args:
        network: NetworkX graph
        
    Returns:
        Dictionary with network statistics
    """
    analysis = {
        "num_nodes": network.number_of_nodes(),
        "num_edges": network.number_of_edges(),
        "density": nx.density(network),
        "is_connected": nx.is_connected(network),
    }
    
    # Add component analysis
    if not nx.is_connected(network):
        components = list(nx.connected_components(network))
        analysis["num_components"] = len(components)
        analysis["largest_component_size"] = len(max(components, key=len))
    
    # Calculate clustering coefficient
    try:
        analysis["avg_clustering"] = nx.average_clustering(network)
    except:
        analysis["avg_clustering"] = None
    
    # Calculate average path length if connected
    if nx.is_connected(network):
        try:
            analysis["avg_path_length"] = nx.average_shortest_path_length(network)
        except:
            analysis["avg_path_length"] = None
    
    return analysis


def identify_hub_genes(network, top_k: int = 5) -> List[tuple]:
    """
    Identify hub genes (highly connected nodes) in the network.
    
    Args:
        network: NetworkX graph
        top_k: Number of top hub genes to return
        
    Returns:
        List of (gene_name, degree) tuples
    """
    gene_degrees = []
    
    for node, data in network.nodes(data=True):
        if data.get('type') == 'gene':
            degree = network.degree(node)
            gene_degrees.append((node, degree))
    
    # Sort by degree and return top k
    gene_degrees.sort(key=lambda x: x[1], reverse=True)
    return gene_degrees[:top_k]


def find_critical_pathways(network, gene_list: List[str]) -> List[str]:
    """
    Identify pathways that connect multiple target genes.
    
    Args:
        network: NetworkX graph
        gene_list: List of gene names
        
    Returns:
        List of critical pathway names
    """
    pathway_connections = {}
    
    for node, data in network.nodes(data=True):
        if data.get('type') == 'pathway':
            # Count how many target genes this pathway connects to
            neighbors = list(network.neighbors(node))
            gene_neighbors = [n for n in neighbors if n in gene_list]
            
            if len(gene_neighbors) > 0:
                pathway_connections[node] = len(gene_neighbors)
    
    # Sort pathways by number of connections
    sorted_pathways = sorted(pathway_connections.items(), key=lambda x: x[1], reverse=True)
    return [pathway for pathway, count in sorted_pathways]
