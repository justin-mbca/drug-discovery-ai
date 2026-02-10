"""
QUICK REFERENCE GUIDE
====================

Lightweight Drug Discovery Multi-Agent System
"""

# Quick Start
# ===========

"""
1. BASIC SETUP
--------------
from agents.design_agent.agent import DesignAgent
from agents.admet_agent.agent import ADMETAgent
from agents.controller_agent.agent import ControllerAgent

design = DesignAgent()
admet = ADMETAgent()
controller = ControllerAgent(goals={"target": 10})


2. ANALYZE COMPOUND
-------------------
# Single compound
result = design.run("aspirin")

# Multiple compounds
compounds = [
    {"cid": "5892", "iupac_name": "compound_name"},
    ...
]
result = design.run(compounds_for_target=compounds)


3. EVALUATE ADMET
-----------------
smiles = "CC(=O)Oc1ccccc1C(=O)O"
if admet.evaluate(smiles):
    design.log_success("aspirin", score=0.85)
else:
    design.log_failure("aspirin", reason="ADMET veto")


4. TRACK PROGRESS
-----------------
while controller.should_continue(iteration, success_count):
    # Work...
    controller.record_success()  # or .record_failure()
    controller.next_iteration()

controller.print_progress()


5. SAVE RESULTS
---------------
design.save_memory()
stats = design.get_stats()
summary = design.get_analysis_summary()
"""

# METHOD REFERENCE
# ================

DESIGN_AGENT_METHODS = {
    # Core Analysis
    "run(compound, compounds_for_target)": "Analyze compound(s)",
    "generate_molecule(target)": "Generate SMILES string",
    "_analyze_single(compound, cid)": "Analyze single compound",
    
    # Memory
    "load_memory()": "Load from disk",
    "save_memory()": "Save to disk",
    "export_memory(filepath)": "Export to custom location",
    "import_memory(filepath)": "Import from file",
    
    # Statistics
    "get_stats()": "Get basic statistics",
    "get_analysis_summary()": "Get comprehensive summary",
    "get_successful_compounds()": "Get all successes",
    "get_failed_compounds()": "Get all failures",
    "get_top_successes(n)": "Get top N compounds",
    
    # Searching
    "search_compound(name)": "Find in history",
    "filter_by_status(status)": "Filter by status",
    
    # Logging
    "log_success(compound, score)": "Log successful compound",
    "log_failure(compound, reason)": "Log failed compound",
    
    # Utility
    "clear_memory()": "Clear all memory",
    "print_summary()": "Print formatted summary",
}

ADMET_AGENT_METHODS = {
    # Evaluation
    "evaluate(smiles)": "Check ADMET pass/fail",
    "evaluate_with_details(smiles)": "Get detailed breakdown",
    
    # Properties
    "get_admet_properties(smiles)": "Get all properties",
    "predict_drug_likeness(smiles)": "Lipinski score",
    "predict_toxicity(smiles)": "Toxicity prediction",
    
    # Batch Operations
    "batch_evaluate(smiles_list)": "Evaluate multiple",
    "filter_compounds(smiles_list)": "Filter library",
    "compare_compounds(smiles_list)": "Compare multiple",
    
    # Analytics
    "get_pass_rate(smiles_list)": "Calculate pass rate",
    "get_evaluation_criteria()": "Get thresholds",
    
    # Reporting
    "print_evaluation_report(smiles)": "Print formatted report",
}

CONTROLLER_AGENT_METHODS = {
    # Stopping
    "stop(success_count, target)": "Check stop criteria",
    "should_continue(iteration, success_count)": "Continue check",
    
    # Tracking
    "record_success()": "Log success",
    "record_failure()": "Log failure",
    "next_iteration()": "Move to next iteration",
    
    # Progress
    "get_progress()": "Get metrics",
    "get_success_rate()": "Success percentage",
    "has_reached_target()": "Target achieved?",
    "has_exceeded_iterations()": "Max iterations?",
    
    # Estimation
    "estimate_completion()": "Est. remaining iterations",
    "get_remaining()": "Get remaining counts",
    "get_performance_metrics()": "Detailed metrics",
    
    # Goals
    "update_goals(new_goals)": "Update targets",
    "get_status()": "Get current state",
    "reset()": "Reset to initial state",
    
    # Reporting
    "log_milestone(text)": "Log milestone",
    "print_progress()": "Print formatted progress",
}

# COMMON PATTERNS
# ===============

PATTERN_SINGLE_ANALYSIS = """
from agents.design_agent.agent import DesignAgent

agent = DesignAgent()
result = agent.run("compound_name")
agent.log_success("compound_name", score=0.85)
agent.save_memory()
"""

PATTERN_BATCH_ANALYSIS = """
from agents.design_agent.agent import DesignAgent

agent = DesignAgent()
compounds = [
    {"cid": "123", "iupac_name": "name1"},
    {"cid": "456", "iupac_name": "name2"},
]
result = agent.run(compounds_for_target=compounds)
agent.save_memory()
"""

PATTERN_FILTERING = """
from agents.admet_agent.agent import ADMETAgent

agent = ADMETAgent()
smiles_list = ["CC(=O)Oc1ccccc1C(=O)O", "..."]
result = agent.filter_compounds(smiles_list)
print(f"Passed: {len(result['passed'])}")
"""

PATTERN_WORKFLOW = """
from agents.design_agent.agent import DesignAgent
from agents.admet_agent.agent import ADMETAgent
from agents.controller_agent.agent import ControllerAgent

design = DesignAgent()
admet = ADMETAgent()
controller = ControllerAgent(goals={"target": 10})

while controller.should_continue(controller.iteration_count, controller.success_count):
    smiles = design.generate_molecule()
    if admet.evaluate(smiles):
        controller.record_success()
        design.log_success(smiles, score=0.8)
    else:
        controller.record_failure()
        design.log_failure(smiles, reason="ADMET veto")
    controller.next_iteration()

design.save_memory()
controller.print_progress()
"""

# MEMORY LOCATIONS
# ================

MEMORY_FILES = {
    "DesignAgent": "agents/design_agent/memory.json",
    "ADMETAgent": "agents/admet_agent/memory.json",
}

# EXAMPLES
# ========

EXAMPLES = {
    "Single compound": "python agents_examples.py 1",
    "Batch analysis": "python agents_examples.py 2",
    "Multi-agent workflow": "python agents_examples.py 3",
    "Compound filtering": "python agents_examples.py 4",
    "Memory management": "python agents_examples.py 5",
    "Progress tracking": "python agents_examples.py 6",
    "Completion estimation": "python agents_examples.py 7",
    "Evaluation report": "python agents_examples.py 8",
}

# IMPORTANT NOTES
# ===============

NOTES = """
✓ DO:
  - Initialize agents without use_tools=True for fast startup
  - Save memory periodically after analyses
  - Use batch_evaluate for multiple compounds
  - Check controller.should_continue() in loops
  - Log successes and failures for tracking

✗ DON'T:
  - Load tools at initialization
  - Forget to save memory
  - Assume all analyses succeed
  - Run infinite loops without stopping criteria
  - Keep large memory objects indefinitely
"""

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "=" * 70)
    print("DESIGN AGENT METHODS")
    print("=" * 70)
    for method, desc in DESIGN_AGENT_METHODS.items():
        print(f"  {method:<40} - {desc}")
    
    print("\n" + "=" * 70)
    print("ADMET AGENT METHODS")
    print("=" * 70)
    for method, desc in ADMET_AGENT_METHODS.items():
        print(f"  {method:<40} - {desc}")
    
    print("\n" + "=" * 70)
    print("CONTROLLER AGENT METHODS")
    print("=" * 70)
    for method, desc in CONTROLLER_AGENT_METHODS.items():
        print(f"  {method:<40} - {desc}")
    
    print("\n" + "=" * 70)
    print("COMMON PATTERNS")
    print("=" * 70)
    print(f"\n1. Single Analysis:\n{PATTERN_SINGLE_ANALYSIS}")
    print(f"\n2. Batch Analysis:\n{PATTERN_BATCH_ANALYSIS}")
    print(f"\n3. Filtering:\n{PATTERN_FILTERING}")
    print(f"\n4. Workflow:\n{PATTERN_WORKFLOW}")
    
    print("\n" + "=" * 70)
    print("EXAMPLES (Run individually)")
    print("=" * 70)
    for desc, cmd in EXAMPLES.items():
        print(f"  {desc:<30} - {cmd}")
    
    print("\n" + "=" * 70)
    print("NOTES")
    print("=" * 70)
    print(NOTES)
