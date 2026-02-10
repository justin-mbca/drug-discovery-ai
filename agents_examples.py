"""
AGENTS USAGE EXAMPLES
====================

Complete working examples for the lightweight drug discovery multi-agent system
"""

# =============================================================================
# EXAMPLE 1: Simple Single Compound Analysis
# =============================================================================
def example_single_compound():
    """Analyze a single compound"""
    from agents.design_agent.agent import DesignAgent
    from agents.admet_agent.agent import ADMETAgent
    
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Single Compound Analysis")
    print("=" * 60)
    
    # Initialize agents
    design = DesignAgent()
    admet = ADMETAgent()
    
    # Analyze aspirin
    compound = "aspirin"
    smiles = "CC(=O)Oc1ccccc1C(=O)O"
    
    print(f"\nAnalyzing {compound}...")
    result = design.run(compound)
    print(f"Status: {result['status']}")
    
    # Evaluate ADMET
    passes = admet.evaluate(smiles)
    print(f"ADMET Pass: {passes}")
    
    # Log results
    if passes:
        design.log_success(compound, score=0.85)
        print("✓ Logged as success")
    else:
        design.log_failure(compound, reason="ADMET filtering")
        print("✗ Logged as failure")
    
    # Save memory
    design.save_memory()
    print("✓ Memory saved")


# =============================================================================
# EXAMPLE 2: Batch Compound Analysis
# =============================================================================
def example_batch_analysis():
    """Analyze multiple compounds at once"""
    from agents.design_agent.agent import DesignAgent
    from agents.admet_agent.agent import ADMETAgent
    
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Batch Compound Analysis")
    print("=" * 60)
    
    # Initialize agents
    design = DesignAgent()
    admet = ADMETAgent()
    
    # Compound list
    compounds = [
        {"cid": "5892", "iupac_name": "2-acetoxybenzoic acid", "name": "aspirin"},
        {"cid": "3672", "iupac_name": "ibuprofen", "name": "ibuprofen"},
        {"cid": "2244", "iupac_name": "acetaminophen", "name": "acetaminophen"}
    ]
    
    print(f"\nAnalyzing {len(compounds)} compounds...")
    result = design.run(compounds_for_target=compounds)
    
    print(f"\n✓ Analyzed {len(result['analyzed_compounds'])} compounds:")
    for compound in result['analyzed_compounds']:
        print(f"   - {compound['compound']}: {compound['status']}")
    
    # Save memory
    design.save_memory()


# =============================================================================
# EXAMPLE 3: Multi-Agent Workflow
# =============================================================================
def example_multi_agent_workflow():
    """Complete multi-agent workflow"""
    from agents.design_agent.agent import DesignAgent
    from agents.admet_agent.agent import ADMETAgent
    from agents.controller_agent.agent import ControllerAgent
    
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Multi-Agent Workflow")
    print("=" * 60)
    
    # Initialize agents
    design = DesignAgent(use_tools=False)
    admet = ADMETAgent(use_tools=False)
    controller = ControllerAgent(goals={"target": 3, "max_iterations": 10})
    
    print(f"\nWorkflow Goal: Find {controller.target_molecules} viable compounds")
    
    # Simulate compound discovery loop
    test_compounds = [
        ("aspirin", "CC(=O)Oc1ccccc1C(=O)O", True),
        ("paracetamol", "CC(=O)Nc1ccc(O)cc1", True),
        ("toxic_compound", "Cl.Cl.Cl.Cl", False),
        ("ibuprofen", "CC(C)Cc1ccc(cc1)C(C)C(=O)O", True),
    ]
    
    for name, smiles, should_pass in test_compounds:
        print(f"\n[{controller.iteration_count + 1}] Analyzing {name}...")
        
        # Design analysis
        design.run(name)
        
        # ADMET evaluation
        passes_admet = admet.evaluate(smiles)
        
        # Log results
        if passes_admet:
            controller.record_success()
            design.log_success(name, score=0.8)
            print(f"   ✓ PASSED ADMET screening")
        else:
            controller.record_failure()
            design.log_failure(name, reason="Failed ADMET")
            print(f"   ✗ FAILED ADMET screening")
        
        controller.next_iteration()
        
        # Check stopping criteria
        if controller.stop(controller.success_count):
            print(f"\n✓ Reached target of {controller.target_molecules} compounds!")
            break
    
    # Print results
    controller.print_progress()
    design.print_summary()
    design.save_memory()


# =============================================================================
# EXAMPLE 4: Compound Filtering
# =============================================================================
def example_compound_filtering():
    """Filter compounds using ADMET agent"""
    from agents.admet_agent.agent import ADMETAgent
    
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Compound Filtering")
    print("=" * 60)
    
    admet = ADMETAgent()
    
    # Compound library
    compounds = [
        "CC(=O)Oc1ccccc1C(=O)O",  # aspirin
        "CC(=O)Nc1ccc(O)cc1",      # paracetamol
        "c1ccccc1c1ccccc1",        # biphenyl
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O",  # ibuprofen
    ]
    
    print(f"\nFiltering {len(compounds)} compounds...")
    result = admet.filter_compounds(compounds, verbose=True)
    
    print(f"\nResults:")
    print(f"  Passed: {result['pass_count']}")
    print(f"  Failed: {result['fail_count']}")
    print(f"  Pass Rate: {result['pass_rate']:.1%}")


# =============================================================================
# EXAMPLE 5: Memory Management
# =============================================================================
def example_memory_management():
    """Manage agent memory"""
    from agents.design_agent.agent import DesignAgent
    
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Memory Management")
    print("=" * 60)
    
    agent = DesignAgent()
    
    # Log some analyses
    print("\nLogging compounds...")
    agent.log_success("compound_a", score=0.9)
    agent.log_success("compound_b", score=0.8)
    agent.log_failure("compound_c", reason="Toxicity")
    agent.log_failure("compound_d", reason="Solubility")
    
    # Get statistics
    print("\nMemory Statistics:")
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get summary
    print("\nAnalysis Summary:")
    summary = agent.get_analysis_summary()
    print(f"  Success Rate: {summary['success_rate']:.1%}")
    print(f"  Avg Score: {summary['average_success_score']:.2f}")
    
    # Get top successes
    print("\nTop Successes:")
    for compound in agent.get_top_successes(2):
        print(f"  - {compound['compound']}: {compound['score']}")
    
    # Export memory
    print("\nExporting memory...")
    agent.export_memory("/tmp/agent_memory.json")
    
    # Save memory
    print("Saving memory...")
    agent.save_memory()


# =============================================================================
# EXAMPLE 6: Progress Tracking
# =============================================================================
def example_progress_tracking():
    """Track workflow progress"""
    from agents.controller_agent.agent import ControllerAgent
    
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Progress Tracking")
    print("=" * 60)
    
    controller = ControllerAgent(goals={"target": 10, "max_iterations": 50})
    
    print("\nSimulating workflow iterations...")
    for i in range(12):
        controller.next_iteration()
        
        # Simulate random successes/failures
        import random
        if random.random() < 0.6:
            controller.record_success()
        else:
            controller.record_failure()
        
        # Print progress every 3 iterations
        if (i + 1) % 3 == 0:
            progress = controller.get_progress()
            print(f"\nIteration {i + 1}:")
            print(f"  Success Rate: {progress['success_rate']:.1%}")
            print(f"  Remaining: {progress['target_remaining']} compounds")
        
        # Check stopping criteria
        if controller.has_reached_target():
            print(f"\n✓ Target reached at iteration {i + 1}!")
            break
    
    # Print final metrics
    controller.print_progress()
    metrics = controller.get_performance_metrics()
    print("Performance Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")


# =============================================================================
# EXAMPLE 7: Estimation and Completion
# =============================================================================
def example_completion_estimation():
    """Estimate workflow completion"""
    from agents.controller_agent.agent import ControllerAgent
    
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Completion Estimation")
    print("=" * 60)
    
    controller = ControllerAgent(goals={"target": 20, "max_iterations": 100})
    
    print("\nSimulating discovery workflow...")
    for i in range(30):
        controller.next_iteration()
        
        # Simulate successes (70% success rate)
        import random
        if random.random() < 0.7:
            controller.record_success()
        else:
            controller.record_failure()
        
        # Estimate after each 10 iterations
        if (i + 1) % 10 == 0:
            estimate = controller.estimate_completion()
            print(f"\nAfter {i + 1} iterations:")
            print(f"  Success Rate: {estimate.get('current_success_rate', 0):.1%}")
            if estimate.get('sufficient_data'):
                print(f"  Estimated Remaining: {estimate.get('estimated_iterations', 0)} iterations")
                print(f"  Achievable: {estimate.get('achievable', False)}")
        
        if controller.has_reached_target():
            print(f"\n✓ Target reached at iteration {i + 1}!")
            break


# =============================================================================
# EXAMPLE 8: Detailed Evaluation Report
# =============================================================================
def example_evaluation_report():
    """Generate detailed evaluation reports"""
    from agents.admet_agent.agent import ADMETAgent
    
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Detailed Evaluation Reports")
    print("=" * 60)
    
    admet = ADMETAgent()
    
    compounds = [
        ("aspirin", "CC(=O)Oc1ccccc1C(=O)O"),
        ("paracetamol", "CC(=O)Nc1ccc(O)cc1"),
    ]
    
    for name, smiles in compounds:
        print(f"\nEvaluating {name}:")
        admet.print_evaluation_report(smiles)


# =============================================================================
# RUN ALL EXAMPLES
# =============================================================================
if __name__ == "__main__":
    import sys
    
    examples = {
        "1": ("Single Compound", example_single_compound),
        "2": ("Batch Analysis", example_batch_analysis),
        "3": ("Multi-Agent Workflow", example_multi_agent_workflow),
        "4": ("Compound Filtering", example_compound_filtering),
        "5": ("Memory Management", example_memory_management),
        "6": ("Progress Tracking", example_progress_tracking),
        "7": ("Completion Estimation", example_completion_estimation),
        "8": ("Evaluation Report", example_evaluation_report),
    }
    
    print("\n" + "=" * 60)
    print("AGENTS USAGE EXAMPLES")
    print("=" * 60)
    print("\nAvailable examples:")
    for key, (desc, _) in examples.items():
        print(f"  {key}. {desc}")
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num in examples:
            _, example_func = examples[example_num]
            try:
                example_func()
                print("\n✓ Example completed successfully!\n")
            except Exception as e:
                print(f"\n✗ Error running example: {e}\n")
                import traceback
                traceback.print_exc()
        else:
            print(f"\n✗ Unknown example: {example_num}\n")
    else:
        # Run all examples
        for key in sorted(examples.keys()):
            try:
                _, example_func = examples[key]
                example_func()
            except Exception as e:
                print(f"\n⚠ Error in example: {e}\n")
