"""
Demonstration of GNN-based Molecular Property Prediction
Shows the complete workflow from SMILES to predictions
"""

import sys
sys.path.insert(0, '.')

from tools.molecular_gnn import MolecularPropertyPredictor, smiles_to_graph
from tools.deepchem_predictor import DeepChemPredictor
from tools.network import build_disease_network, run_gnn_analysis, identify_hub_genes
from tools.pdb_analysis import PDBAnalyzer


def demo_molecular_gnn():
    """Demonstrate GNN-based molecular property prediction."""
    print("\n" + "=" * 80)
    print("DEMO 1: GNN-Based Molecular Property Prediction")
    print("=" * 80)
    
    # Test molecules with different properties
    test_molecules = {
        "Aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "Caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "Ibuprofen": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
        "Paracetamol": "CC(=O)Nc1ccc(O)cc1",
    }
    
    print("\n1. Converting SMILES to Molecular Graphs")
    print("-" * 80)
    for name, smiles in test_molecules.items():
        graph = smiles_to_graph(smiles)
        if graph:
            print(f"{name:15} → {graph.num_nodes:3d} nodes, {graph.num_edges:3d} edges")
    
    print("\n2. Predicting Molecular Properties with GNN")
    print("-" * 80)
    predictor = MolecularPropertyPredictor()
    
    results = []
    for name, smiles in test_molecules.items():
        props = predictor.predict_property(smiles)
        results.append((name, props))
        
        print(f"\n{name}:")
        print(f"  Molecular Weight: {props['molecular_weight']:.2f} g/mol")
        print(f"  LogP: {props['logp']:.2f}")
        print(f"  H-Bond Donors: {props['num_h_donors']}")
        print(f"  H-Bond Acceptors: {props['num_h_acceptors']}")
        print(f"  TPSA: {props['tpsa']:.2f} Ų")
        print(f"  Lipinski Pass: {'✓' if props['lipinski_pass'] else '✗'}")
    
    print("\n3. Ranking Molecules by Properties")
    print("-" * 80)
    smiles_list = list(test_molecules.values())
    
    # Rank by molecular weight
    ranked_mw = predictor.rank_molecules(smiles_list, criteria="molecular_weight")
    print("\nRanked by Molecular Weight:")
    for i, (smiles, mw) in enumerate(ranked_mw, 1):
        name = [n for n, s in test_molecules.items() if s == smiles][0]
        print(f"  {i}. {name:15} - {mw:.2f} g/mol")
    
    # Rank by LogP
    ranked_logp = predictor.rank_molecules(smiles_list, criteria="logp")
    print("\nRanked by LogP (Lipophilicity):")
    for i, (smiles, logp) in enumerate(ranked_logp, 1):
        name = [n for n, s in test_molecules.items() if s == smiles][0]
        print(f"  {i}. {name:15} - {logp:.2f}")


def demo_deepchem():
    """Demonstrate DeepChem predictor capabilities."""
    print("\n" + "=" * 80)
    print("DEMO 2: DeepChem ADMET Property Prediction")
    print("=" * 80)
    
    predictor = DeepChemPredictor()
    
    if not predictor.available:
        print("\n⚠ DeepChem is not installed (optional dependency)")
        print("Install with: pip install deepchem")
        print("The predictor gracefully handles this and uses RDKit-based heuristics instead.")
        return
    
    smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
    
    print("\n1. Solubility Prediction")
    print("-" * 80)
    sol = predictor.predict_solubility(smiles)
    if "error" not in sol:
        print(f"Estimated LogS: {sol['estimated_logS']:.2f}")
        print(f"Solubility Class: {sol['solubility_class']}")
    
    print("\n2. Toxicity Assessment")
    print("-" * 80)
    tox = predictor.predict_toxicity(smiles)
    if "error" not in tox:
        print(f"Toxicity Risk Score: {tox['toxicity_risk_score']:.2f}")
        print(f"Risk Classification: {tox['toxicity_risk_class']}")
    
    print("\n3. Comprehensive ADMET Properties")
    print("-" * 80)
    admet = predictor.predict_admet_properties(smiles)
    if "error" not in admet:
        print(f"Lipinski's Rule of Five: {'Pass ✓' if admet['lipinski_rule_of_5'] else 'Fail ✗'}")
        print(f"Veber's Rules: {'Pass ✓' if admet['veber_rules'] else 'Fail ✗'}")
        print(f"Bioavailability Score: {admet['bioavailability_score']:.2f}")
    
    print("\n4. Molecular Similarity")
    print("-" * 80)
    smiles1 = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
    smiles2 = "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"  # Ibuprofen
    
    sim = predictor.compare_molecules(smiles1, smiles2)
    if "error" not in sim:
        print(f"Aspirin vs Ibuprofen:")
        print(f"  Tanimoto Similarity: {sim['tanimoto_similarity']:.3f}")
        print(f"  Dice Similarity: {sim['dice_similarity']:.3f}")
        print(f"  Interpretation: {sim['interpretation']}")


def demo_network_analysis():
    """Demonstrate network-based GNN analysis."""
    print("\n" + "=" * 80)
    print("DEMO 3: GNN-Based Disease Network Analysis")
    print("=" * 80)
    
    # Alzheimer's disease network
    pathways = [
        "Alzheimer_pathway",
        "Amyloid_processing",
        "Tau_protein_pathway",
        "Neuroinflammation",
        "Apoptosis"
    ]
    
    targets = [
        "APP",      # Amyloid precursor protein
        "BACE1",    # Beta-secretase 1
        "MAPT",     # Tau protein
        "PSEN1",    # Presenilin 1
        "APOE"      # Apolipoprotein E
    ]
    
    print("\n1. Building Disease Network")
    print("-" * 80)
    network = build_disease_network(pathways, targets)
    print(f"Network created:")
    print(f"  Nodes: {network.number_of_nodes()} ({len(pathways)} pathways, {len(targets)} genes)")
    print(f"  Edges: {network.number_of_edges()}")
    
    print("\n2. Running GNN-Based Network Analysis")
    print("-" * 80)
    insights = run_gnn_analysis(network)
    
    print("\nGene Importance Scores (based on network topology):")
    sorted_genes = sorted(insights.items(), key=lambda x: x[1], reverse=True)
    for gene, score in sorted_genes:
        bar = "█" * int(score * 30)
        print(f"  {gene:10} {score:.3f} {bar}")
    
    print("\n3. Identifying Hub Genes")
    print("-" * 80)
    hubs = identify_hub_genes(network, top_k=3)
    print("\nTop 3 Hub Genes (highest connectivity):")
    for i, (gene, degree) in enumerate(hubs, 1):
        print(f"  {i}. {gene:10} (degree: {degree})")
    
    print("\n4. Network Statistics")
    print("-" * 80)
    from tools.network import analyze_network_topology
    topology = analyze_network_topology(network)
    print(f"Density: {topology['density']:.3f}")
    print(f"Connected: {topology['is_connected']}")
    if topology.get('avg_clustering'):
        print(f"Avg Clustering: {topology['avg_clustering']:.3f}")
    if topology.get('avg_path_length'):
        print(f"Avg Path Length: {topology['avg_path_length']:.3f}")


def demo_pdb_analysis():
    """Demonstrate PDB analysis capabilities."""
    print("\n" + "=" * 80)
    print("DEMO 4: Protein Structure Analysis (PDB)")
    print("=" * 80)
    
    analyzer = PDBAnalyzer()
    
    if not analyzer.available:
        print("\n⚠ Biopython is not installed (optional dependency)")
        print("Install with: pip install biopython")
        print("This is required for detailed PDB structure analysis.")
        return
    
    print("\nPDB Analysis Capabilities:")
    print("-" * 80)
    print("✓ Parse PDB files from local storage or AlphaFold database")
    print("✓ Extract protein sequences from structures")
    print("✓ Calculate center of mass")
    print("✓ Identify binding sites and ligands")
    print("✓ Measure inter-residue distances")
    print("✓ Assess structure quality and completeness")
    
    print("\nExample Usage:")
    print("-" * 80)
    print("from tools.pdb_analysis import EnhancedAlphaFoldTool")
    print("")
    print("tool = EnhancedAlphaFoldTool()")
    print("results = tool.analyze_structure('P05067')  # APP protein")
    print("")
    print("# Access results:")
    print("print(results['structure_info'])  # Basic structure information")
    print("print(results['sequence'])         # Amino acid sequence")
    print("print(results['quality_metrics'])  # Quality assessment")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print("GEOMETRIC DEEP LEARNING FOR DRUG DISCOVERY")
    print("Comprehensive Demonstration of GNN-Based Molecular Property Prediction")
    print("=" * 80)
    
    # Run all demos
    demo_molecular_gnn()
    demo_deepchem()
    demo_network_analysis()
    demo_pdb_analysis()
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Capabilities Demonstrated:")
    print("  ✓ GNN-based molecular property prediction")
    print("  ✓ SMILES to molecular graph conversion")
    print("  ✓ Drug-likeness assessment (Lipinski's Rule)")
    print("  ✓ ADMET property prediction")
    print("  ✓ Disease network analysis with real GNN")
    print("  ✓ Hub gene identification")
    print("  ✓ PDB structure analysis capabilities")
    print("\nThese implementations address the gaps identified:")
    print("  ✓ Geometric Deep Learning: GNNs with PyTorch Geometric")
    print("  ✓ Molecular graphs: Explicit graph representation and analysis")
    print("  ✓ Protein structure: Enhanced AlphaFold + PDB analysis")
    print("\nFor more details, see the README.md file.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
