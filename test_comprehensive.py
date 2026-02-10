#!/usr/bin/env python3
"""
Comprehensive test suite for lightweight drug discovery agents.
Tests all major functionality: initialization, methods, workflows, memory, and edge cases.
"""

import json
import time
import os
import sys
from pathlib import Path

# Test results tracking
test_results = {
    'passed': [],
    'failed': [],
    'errors': []
}

def log_test(name, status, message=""):
    """Log test result"""
    print(f"{'✓' if status else '✗'} {name}")
    if message:
        print(f"  └─ {message}")
    
    if status:
        test_results['passed'].append(name)
    else:
        test_results['failed'].append((name, message))

def log_error(name, exception):
    """Log error during test"""
    print(f"⚠ {name}")
    print(f"  └─ ERROR: {str(exception)}")
    test_results['errors'].append((name, str(exception)))

def print_section(title):
    """Print test section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_summary():
    """Print test summary"""
    print(f"\n{'='*60}")
    print(f"  TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✓ Passed: {len(test_results['passed'])}")
    print(f"✗ Failed: {len(test_results['failed'])}")
    print(f"⚠ Errors: {len(test_results['errors'])}")
    total = len(test_results['passed']) + len(test_results['failed']) + len(test_results['errors'])
    print(f"Total:  {total}")
    
    if test_results['failed']:
        print(f"\nFailed Tests:")
        for name, msg in test_results['failed']:
            print(f"  - {name}: {msg}")
    
    if test_results['errors']:
        print(f"\nErrors:")
        for name, msg in test_results['errors']:
            print(f"  - {name}: {msg}")

# ============================================================================
# TEST 1: IMPORTS & INITIALIZATION
# ============================================================================

print_section("TEST 1: IMPORTS & INITIALIZATION")

try:
    from agents.design_agent.agent import DesignAgent
    log_test("Import DesignAgent", True)
except Exception as e:
    log_error("Import DesignAgent", e)

try:
    from agents.admet_agent.agent import ADMETAgent
    log_test("Import ADMETAgent", True)
except Exception as e:
    log_error("Import ADMETAgent", e)

try:
    from agents.controller_agent.agent import ControllerAgent
    log_test("Import ControllerAgent", True)
except Exception as e:
    log_error("Import ControllerAgent", e)

# Test instantiation without tools (should be fast)
try:
    start = time.time()
    design_agent = DesignAgent(use_tools=False)
    elapsed = time.time() - start
    log_test("Instantiate DesignAgent (no tools)", elapsed < 1.0, f"Time: {elapsed:.3f}s")
except Exception as e:
    log_error("Instantiate DesignAgent", e)

try:
    start = time.time()
    admet_agent = ADMETAgent(use_tools=False)
    elapsed = time.time() - start
    log_test("Instantiate ADMETAgent (no tools)", elapsed < 1.0, f"Time: {elapsed:.3f}s")
except Exception as e:
    log_error("Instantiate ADMETAgent", e)

try:
    start = time.time()
    controller = ControllerAgent()
    elapsed = time.time() - start
    log_test("Instantiate ControllerAgent", elapsed < 0.1, f"Time: {elapsed:.3f}s")
except Exception as e:
    log_error("Instantiate ControllerAgent", e)

# ============================================================================
# TEST 2: DESIGN AGENT METHODS
# ============================================================================

print_section("TEST 2: DESIGN AGENT METHODS")

try:
    design_agent = DesignAgent(use_tools=False)
    
    # Test run method
    try:
        result = design_agent.run(compound="TestCompound")
        log_test("DesignAgent.run()", isinstance(result, (str, dict)))
    except Exception as e:
        log_error("DesignAgent.run()", e)
    
    # Test molecule generation
    try:
        mol = design_agent.generate_molecule(target="HTARget")
        log_test("DesignAgent.generate_molecule()", mol is None or isinstance(mol, str))
    except Exception as e:
        log_error("DesignAgent.generate_molecule()", e)
    
    # Test compound search
    try:
        results = design_agent.search_compound("benzene")
        log_test("DesignAgent.search_compound()", results is None or isinstance(results, dict))
    except Exception as e:
        log_error("DesignAgent.search_compound()", e)
    
    # Test filtering
    try:
        filtered = design_agent.filter_by_status("completed")
        log_test("DesignAgent.filter_by_status()", isinstance(filtered, list))
    except Exception as e:
        log_error("DesignAgent.filter_by_status()", e)
    
    # Test memory operations
    try:
        design_agent.load_memory()
        log_test("DesignAgent.load_memory()", True)
    except Exception as e:
        log_error("DesignAgent.load_memory()", e)
    
    try:
        stats = design_agent.get_stats()
        log_test("DesignAgent.get_stats()", isinstance(stats, dict))
    except Exception as e:
        log_error("DesignAgent.get_stats()", e)
    
    try:
        summary = design_agent.get_analysis_summary()
        log_test("DesignAgent.get_analysis_summary()", isinstance(summary, dict))
    except Exception as e:
        log_error("DesignAgent.get_analysis_summary()", e)
    
    # Test logging (correct signatures)
    try:
        design_agent.log_success("test_compound", 0.95)
        log_test("DesignAgent.log_success()", True)
    except Exception as e:
        log_error("DesignAgent.log_success()", e)
    
    try:
        design_agent.log_failure("test_compound_fail", "reason")
        log_test("DesignAgent.log_failure()", True)
    except Exception as e:
        log_error("DesignAgent.log_failure()", e)
    
    # Test get top successes
    try:
        tops = design_agent.get_top_successes(n=5)
        log_test("DesignAgent.get_top_successes()", isinstance(tops, list))
    except Exception as e:
        log_error("DesignAgent.get_top_successes()", e)
    
except Exception as e:
    log_error("DesignAgent initialization for method tests", e)

# ============================================================================
# TEST 3: ADMET AGENT METHODS
# ============================================================================

print_section("TEST 3: ADMET AGENT METHODS")

try:
    admet_agent = ADMETAgent(use_tools=False)
    
    # Test evaluation
    try:
        props = admet_agent.get_admet_properties("CC")
        log_test("ADMETAgent.get_admet_properties()", isinstance(props, dict))
    except Exception as e:
        log_error("ADMETAgent.get_admet_properties()", e)
    
    # Test drug likeness
    try:
        likelihood = admet_agent.predict_drug_likeness("CC")
        log_test("ADMETAgent.predict_drug_likeness()", isinstance(likelihood, (str, dict)))
    except Exception as e:
        log_error("ADMETAgent.predict_drug_likeness()", e)
    
    # Test toxicity
    try:
        toxicity = admet_agent.predict_toxicity("CC")
        log_test("ADMETAgent.predict_toxicity()", isinstance(toxicity, (str, dict)))
    except Exception as e:
        log_error("ADMETAgent.predict_toxicity()", e)
    
    # Test batch evaluation
    try:
        batch_results = admet_agent.batch_evaluate(["CC", "CCC"])
        log_test("ADMETAgent.batch_evaluate()", isinstance(batch_results, (list, dict)))
    except Exception as e:
        log_error("ADMETAgent.batch_evaluate()", e)
    
    # Test filtering (correct signature)
    try:
        filtered = admet_agent.filter_compounds(["CC", "CCC"])
        log_test("ADMETAgent.filter_compounds()", isinstance(filtered, (list, dict)))
    except Exception as e:
        log_error("ADMETAgent.filter_compounds()", e)
    
    # Test comparison
    try:
        comparison = admet_agent.compare_compounds(["CC", "CCC"])
        log_test("ADMETAgent.compare_compounds()", isinstance(comparison, (dict, list)))
    except Exception as e:
        log_error("ADMETAgent.compare_compounds()", e)
    
    # Test pass rate (correct signature)
    try:
        rate = admet_agent.get_pass_rate(["CC", "CCC"])
        log_test("ADMETAgent.get_pass_rate()", isinstance(rate, (int, float)))
    except Exception as e:
        log_error("ADMETAgent.get_pass_rate()", e)
    
    # Test criteria
    try:
        criteria = admet_agent.get_evaluation_criteria()
        log_test("ADMETAgent.get_evaluation_criteria()", isinstance(criteria, dict))
    except Exception as e:
        log_error("ADMETAgent.get_evaluation_criteria()", e)
    
except Exception as e:
    log_error("ADMETAgent initialization for method tests", e)

# ============================================================================
# TEST 4: CONTROLLER AGENT METHODS
# ============================================================================

print_section("TEST 4: CONTROLLER AGENT METHODS")

try:
    controller = ControllerAgent()
    
    # Test progress tracking
    try:
        controller.record_success()
        log_test("ControllerAgent.record_success()", True)
    except Exception as e:
        log_error("ControllerAgent.record_success()", e)
    
    try:
        controller.record_failure()
        log_test("ControllerAgent.record_failure()", True)
    except Exception as e:
        log_error("ControllerAgent.record_failure()", e)
    
    try:
        progress = controller.get_progress()
        log_test("ControllerAgent.get_progress()", isinstance(progress, dict))
    except Exception as e:
        log_error("ControllerAgent.get_progress()", e)
    
    try:
        rate = controller.get_success_rate()
        log_test("ControllerAgent.get_success_rate()", isinstance(rate, (int, float)))
    except Exception as e:
        log_error("ControllerAgent.get_success_rate()", e)
    
    try:
        # Test should_continue with proper arguments
        should_cont = controller.should_continue(iteration=1, success_count=1)
        log_test("ControllerAgent.should_continue()", isinstance(should_cont, bool))
    except Exception as e:
        log_error("ControllerAgent.should_continue()", e)
    
    try:
        next_iter = controller.next_iteration()
        log_test("ControllerAgent.next_iteration()", isinstance(next_iter, int) or next_iter is None)
    except Exception as e:
        log_error("ControllerAgent.next_iteration()", e)
    
    try:
        reached = controller.has_reached_target()
        log_test("ControllerAgent.has_reached_target()", isinstance(reached, bool))
    except Exception as e:
        log_error("ControllerAgent.has_reached_target()", e)
    
    try:
        estimate = controller.estimate_completion()
        log_test("ControllerAgent.estimate_completion()", isinstance(estimate, (str, dict, float)))
    except Exception as e:
        log_error("ControllerAgent.estimate_completion()", e)
    
except Exception as e:
    log_error("ControllerAgent initialization for method tests", e)

# ============================================================================
# TEST 5: MEMORY PERSISTENCE
# ============================================================================

print_section("TEST 5: MEMORY PERSISTENCE")

try:
    design_agent = DesignAgent(use_tools=False)
    
    # Add some test data (correct signature)
    design_agent.log_success("TestMol1", 0.9)
    design_agent.log_success("TestMol2", 0.85)
    
    try:
        design_agent.save_memory()
        log_test("DesignAgent.save_memory()", True)
    except Exception as e:
        log_error("DesignAgent.save_memory()", e)
    
    try:
        # Create new agent and load memory
        design_agent2 = DesignAgent(use_tools=False)
        design_agent2.load_memory()
        stats = design_agent2.get_stats()
        has_data = stats.get('total_successes', 0) > 0
        log_test("DesignAgent memory persistence", has_data)
    except Exception as e:
        log_error("DesignAgent memory persistence", e)
    
    try:
        export_path = "/tmp/agent_memory_export.json"
        exported = design_agent.export_memory(export_path)
        log_test("DesignAgent.export_memory()", isinstance(exported, bool))
    except Exception as e:
        log_error("DesignAgent.export_memory()", e)
    
    try:
        design_agent.clear_memory()
        log_test("DesignAgent.clear_memory()", True)
    except Exception as e:
        log_error("DesignAgent.clear_memory()", e)
    
except Exception as e:
    log_error("Memory persistence tests", e)

# ============================================================================
# TEST 6: MULTI-AGENT WORKFLOW
# ============================================================================

print_section("TEST 6: MULTI-AGENT WORKFLOW")

try:
    design_agent = DesignAgent(use_tools=False)
    admet_agent = ADMETAgent(use_tools=False)
    controller = ControllerAgent()
    
    # Simulate workflow
    test_compounds = ["CC", "CCC", "CCCC"]
    
    try:
        # Step 1: Design generates compounds (correct signature)
        for compound in test_compounds:
            design_agent.log_success(compound, 0.8)
        controller.record_success()
        
        log_test("Workflow Step 1: Design agent compounds", True)
    except Exception as e:
        log_error("Workflow Step 1", e)
    
    try:
        # Step 2: ADMET evaluates compounds
        results = admet_agent.batch_evaluate(test_compounds)
        controller.record_success()
        
        log_test("Workflow Step 2: ADMET evaluation", True)
    except Exception as e:
        log_error("Workflow Step 2", e)
    
    try:
        # Step 3: Controller tracks progress (with correct args)
        progress = controller.get_progress()
        should_continue = controller.should_continue(iteration=1, success_count=2)
        success_rate = controller.get_success_rate()
        
        workflow_ok = isinstance(progress, dict) and isinstance(should_continue, bool) and isinstance(success_rate, (int, float))
        log_test("Workflow Step 3: Controller orchestration", workflow_ok)
    except Exception as e:
        log_error("Workflow Step 3", e)
    
except Exception as e:
    log_error("Multi-agent workflow", e)

# ============================================================================
# TEST 7: EXAMPLES VALIDATION
# ============================================================================

print_section("TEST 7: EXAMPLES VALIDATION")

try:
    # Import examples
    import importlib.util
    spec = importlib.util.spec_from_file_location("agents_examples", "agents_examples.py")
    examples = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(examples)
        log_test("Import agents_examples.py", True)
    except Exception as e:
        log_error("Import agents_examples.py", e)
    
    # Try to run examples (they might not all work without full setup)
    try:
        # Example 1: Single analysis
        if hasattr(examples, 'example_single_compound_analysis'):
            examples.example_single_compound_analysis()
            log_test("Example 1: Single compound analysis", True)
    except Exception as e:
        log_error("Example 1", e)
    
except Exception as e:
    log_error("Examples module", e)

# ============================================================================
# TEST 8: ERROR HANDLING & EDGE CASES
# ============================================================================

print_section("TEST 8: ERROR HANDLING & EDGE CASES")

try:
    design_agent = DesignAgent(use_tools=False)
    
    # Test with empty input
    try:
        result = design_agent.search_compound("")
        log_test("DesignAgent: Empty string search", True)
    except Exception as e:
        log_error("DesignAgent: Empty string search", e)
    
    # Test with None
    try:
        result = design_agent.filter_by_status(None)
        log_test("DesignAgent: None input", True)
    except Exception as e:
        log_error("DesignAgent: None input", e)
    
except Exception as e:
    log_error("Edge case tests", e)

try:
    admet_agent = ADMETAgent(use_tools=False)
    
    # Test batch with empty list
    try:
        result = admet_agent.batch_evaluate([])
        log_test("ADMETAgent: Empty batch", True)
    except Exception as e:
        log_error("ADMETAgent: Empty batch", e)
    
except Exception as e:
    log_error("ADMET edge cases", e)

# ============================================================================
# TEST 9: PERFORMANCE
# ============================================================================

print_section("TEST 9: PERFORMANCE")

try:
    # Startup time
    start = time.time()
    design_agent = DesignAgent(use_tools=False)
    startup_time = time.time() - start
    
    startup_ok = startup_time < 0.5
    log_test("DesignAgent startup time", startup_ok, f"{startup_time:.3f}s (target: <0.5s)")
    
    # Method execution time
    start = time.time()
    for i in range(100):
        design_agent.get_stats()
    method_time = (time.time() - start) / 100
    
    method_ok = method_time < 0.01
    log_test("DesignAgent method execution (100 calls)", method_ok, f"Avg: {method_time*1000:.3f}ms")
    
except Exception as e:
    log_error("Performance tests", e)

# ============================================================================
# SUMMARY
# ============================================================================

print_summary()

# Exit with appropriate code
exit_code = 0 if len(test_results['failed']) == 0 and len(test_results['errors']) == 0 else 1
sys.exit(exit_code)
