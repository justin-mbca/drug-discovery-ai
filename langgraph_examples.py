"""
LangGraph Drug Discovery Examples

Demonstrates the LangGraph-based agent system with ReAct reasoning,
conditional routing, and state management.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.langgraph_agents import (
    LangGraphDrugDiscoveryAgent,
    LANGGRAPH_AVAILABLE
)


def example_1_basic_analysis():
    """Example 1: Basic compound analysis with reasoning traces"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Compound Analysis with ReAct Reasoning")
    print("=" * 70)
    
    if not LANGGRAPH_AVAILABLE:
        print("\n❌ LangGraph not available. Install with:")
        print("   pip install langgraph langchain-core langchain-openai")
        return
    
    # Create agent
    agent = LangGraphDrugDiscoveryAgent(max_iterations=5, target_successes=1)
    
    # Analyze aspirin
    print("\n🔬 Analyzing: Aspirin")
    print("SMILES: CC(=O)Oc1ccccc1C(=O)O\n")
    
    result = agent.analyze_compound("aspirin", smiles="CC(=O)Oc1ccccc1C(=O)O")
    
    # Show reasoning trace
    print("\n📋 Reasoning Trace:")
    print("-" * 70)
    traces = agent.get_reasoning_trace(result)
    for i, trace in enumerate(traces, 1):
        print(f"{i}. {trace}")
    
    # Show final result
    if result:
        final_state = list(result.values())[-1]
        print("\n" + "=" * 70)
        print("📊 FINAL RESULTS")
        print("=" * 70)
        print(f"✓ Compound: {final_state.get('compound')}")
        print(f"✓ Decision: {final_state.get('final_decision')}")
        print(f"✓ Confidence: {final_state.get('confidence_score'):.2%}")
        print(f"✓ Iterations: {final_state.get('iteration')}")
        print(f"✓ Success Count: {final_state.get('success_count')}")
        print(f"✓ Failure Count: {final_state.get('failure_count')}")


def example_2_multi_compound_workflow():
    """Example 2: Multi-compound workflow with state tracking"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multi-Compound Workflow")
    print("=" * 70)
    
    if not LANGGRAPH_AVAILABLE:
        print("\n❌ LangGraph not available.")
        return
    
    compounds = [
        ("aspirin", "CC(=O)Oc1ccccc1C(=O)O"),
        ("paracetamol", "CC(=O)Nc1ccc(O)cc1"),
        ("ibuprofen", "CC(C)Cc1ccc(cc1)C(C)C(=O)O")
    ]
    
    agent = LangGraphDrugDiscoveryAgent(max_iterations=3, target_successes=2)
    
    results = []
    for name, smiles in compounds:
        print(f"\n🔬 Analyzing: {name}")
        print(f"   SMILES: {smiles}")
        
        result = agent.analyze_compound(name, smiles=smiles)
        
        if result:
            final_state = list(result.values())[-1]
            decision = final_state.get('final_decision', 'UNKNOWN')
            confidence = final_state.get('confidence_score', 0)
            
            results.append({
                "compound": name,
                "decision": decision,
                "confidence": confidence
            })
            
            print(f"   → Decision: {decision} (confidence: {confidence:.2%})")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 WORKFLOW SUMMARY")
    print("=" * 70)
    
    approved = [r for r in results if r["decision"] == "APPROVED"]
    rejected = [r for r in results if r["decision"] == "REJECTED"]
    
    print(f"✅ Approved: {len(approved)}/{len(results)}")
    for compound in approved:
        print(f"   • {compound['compound']} ({compound['confidence']:.2%})")
    
    print(f"\n❌ Rejected: {len(rejected)}/{len(results)}")
    for compound in rejected:
        print(f"   • {compound['compound']}")


def example_3_export_reasoning_traces():
    """Example 3: Export detailed reasoning traces"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Export Reasoning Traces")
    print("=" * 70)
    
    if not LANGGRAPH_AVAILABLE:
        print("\n❌ LangGraph not available.")
        return
    
    agent = LangGraphDrugDiscoveryAgent(max_iterations=5, target_successes=1)
    
    print("\n🔬 Analyzing: Caffeine")
    result = agent.analyze_compound("caffeine", smiles="CN1C=NC2=C1C(=O)N(C(=O)N2C)C")
    
    # Export to file
    export_path = "/tmp/caffeine_langgraph_analysis.json"
    agent.export_results(result, export_path)
    
    print(f"\n✅ Analysis complete!")
    print(f"📁 Results exported to: {export_path}")
    print(f"\nThe export includes:")
    print("   • Final decision and confidence")
    print("   • Complete reasoning trace (ReAct pattern)")
    print("   • Design, ADMET, and validation results")
    print("   • Iteration and success tracking")


def example_4_conditional_routing_demo():
    """Example 4: Demonstrate conditional routing based on results"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Conditional Routing Demo")
    print("=" * 70)
    
    if not LANGGRAPH_AVAILABLE:
        print("\n❌ LangGraph not available.")
        return
    
    print("\nThis example shows how the graph conditionally routes based on:")
    print("✓ Design analysis results → routes to ADMET or validation")
    print("✓ ADMET evaluation → routes to validation or decision")
    print("✓ Decision node → routes to continue or end")
    
    agent = LangGraphDrugDiscoveryAgent(max_iterations=10, target_successes=1)
    
    print("\n🔬 Analyzing compound with routing traces...\n")
    result = agent.analyze_compound("test_compound", smiles="CCCCCC")
    
    # Extract routing decisions from reasoning trace
    if result:
        traces = agent.get_reasoning_trace(result)
        routing_traces = [t for t in traces if "Proceeding to" in t or "next" in t.lower()]
        
        print("🔀 Routing Decisions:")
        print("-" * 70)
        for i, trace in enumerate(routing_traces, 1):
            print(f"{i}. {trace}")
    
    print("\n✅ Demo complete. Graph automatically routed between nodes based on results.")


def example_5_checkpointing_demo():
    """Example 5: Demonstrate state checkpointing"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: State Checkpointing Demo")
    print("=" * 70)
    
    if not LANGGRAPH_AVAILABLE:
        print("\n❌ LangGraph not available.")
        return
    
    print("\nLangGraph automatically checkpoints state at each node.")
    print("This enables:")
    print("✓ Resume from any point in the workflow")
    print("✓ Replay past decisions")
    print("✓ Debug specific nodes")
    print("✓ Audit trail for compliance")
    
    agent = LangGraphDrugDiscoveryAgent(max_iterations=3, target_successes=1)
    
    print("\n🔬 Running workflow with checkpointing...")
    result = agent.analyze_compound("checkpoint_test", smiles="CC(C)CC")
    
    print("\n✅ Checkpointing active!")
    print(f"   Thread ID: {agent.thread_id}")
    print("   All state transitions are preserved in memory")


def run_all_examples():
    """Run all examples"""
    examples = [
        ("1", example_1_basic_analysis),
        ("2", example_2_multi_compound_workflow),
        ("3", example_3_export_reasoning_traces),
        ("4", example_4_conditional_routing_demo),
        ("5", example_5_checkpointing_demo),
    ]
    
    print("\n" + "=" * 70)
    print("LangGraph Drug Discovery Examples")
    print("=" * 70)
    print("\nAvailable examples:")
    for num, func in examples:
        print(f"  {num}. {func.__doc__.split(':')[1].strip()}")
    print("  all. Run all examples")
    
    choice = input("\nSelect example (1-5, all): ").strip().lower()
    
    if choice == "all":
        for _, func in examples:
            func()
    elif choice in [num for num, _ in examples]:
        for num, func in examples:
            if choice == num:
                func()
                break
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        
        examples = {
            "1": example_1_basic_analysis,
            "2": example_2_multi_compound_workflow,
            "3": example_3_export_reasoning_traces,
            "4": example_4_conditional_routing_demo,
            "5": example_5_checkpointing_demo,
        }
        
        if example_num in examples:
            examples[example_num]()
        elif example_num.lower() == "all":
            for func in examples.values():
                func()
        else:
            print(f"Unknown example: {example_num}")
            print("Available: 1, 2, 3, 4, 5, all")
    else:
        run_all_examples()
