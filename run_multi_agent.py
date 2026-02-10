"""
Lightweight multi-agent integration test
- Tests design, ADMET, and controller agents
- No heavy ML dependencies at import time
- Fast execution for testing and validation
"""

from agents.design_agent.agent import DesignAgent
from agents.admet_agent.agent import ADMETAgent
from agents.controller_agent.agent import ControllerAgent


def run_agents():
    """Run multi-agent system with lightweight agents"""
    print("=" * 60)
    print("LIGHTWEIGHT MULTI-AGENT DRUG DISCOVERY SYSTEM")
    print("=" * 60)
    
    # Initialize agents
    print("\n1. Initializing agents...")
    design_agent = DesignAgent(use_tools=False)  # Fast initialization
    admet_agent = ADMETAgent(use_tools=False)
    controller = ControllerAgent(goals={"target": 5})
    
    print("✓ Agents initialized successfully")
    print(f"   - DesignAgent: {design_agent}")
    print(f"   - ADMETAgent: {admet_agent}")
    print(f"   - ControllerAgent: {controller}")
    
    # Display controller status
    print("\n2. Workflow Status:")
    status = controller.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Test compound analysis (simulated)
    print("\n3. Testing compound analysis...")
    test_compounds = [
        {"cid": "5892", "name": "aspirin", "iupac_name": "2-acetoxybenzoic acid"},
        {"cid": "3672", "name": "ibuprofen", "iupac_name": "2-(4-(2-methylpropyl)phenyl)propionic acid"},
    ]
    
    for compound in test_compounds:
        name = compound["name"]
        print(f"\n   Analyzing {name}...")
        
        # Design agent analyzes
        result = design_agent._analyze_single(name, compound["cid"])
        print(f"   ✓ Design analysis: {result['status']}")
        
        # ADMET evaluation (would use SMILES in real scenario)
        passes_admet = admet_agent.evaluate(name)
        print(f"   ✓ ADMET evaluation: {'PASS' if passes_admet else 'FAIL'}")
        
        # Track in controller
        if passes_admet:
            controller.record_success()
            design_agent.log_success(name, score=0.85)
        else:
            controller.record_failure()
            design_agent.log_failure(name, reason="ADMET veto")
    
    # Display final results
    print("\n4. Final Results:")
    print(f"   Compounds analyzed: {len(test_compounds)}")
    print(f"   Compounds passed: {controller.success_count}")
    print(f"   Compounds failed: {controller.failure_count}")
    
    # Save agent memory
    print("\n5. Saving agent memory...")
    design_agent.save_memory()
    print("✓ Memory saved")
    
    # Display statistics
    print("\n6. Agent Statistics:")
    stats = design_agent.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✓ Multi-agent integration test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_agents()
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
