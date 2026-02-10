# Drug Discovery Multi-Agent System

Fast, lightweight, no heavy ML dependencies at startup.

## Quick Start

```python
from agents.design_agent.agent import DesignAgent
from agents.admet_agent.agent import ADMETAgent
from agents.controller_agent.agent import ControllerAgent

# Initialize agents (instant startup - no heavy imports)
design = DesignAgent()
admet = ADMETAgent()
controller = ControllerAgent(goals={"target": 10})

# Analyze compounds
result = design.run("aspirin")

# Evaluate ADMET properties
if admet.evaluate("CC(=O)Oc1ccccc1C(=O)O"):
    design.log_success("aspirin", score=0.85)
else:
    design.log_failure("aspirin", reason="ADMET veto")

# Track workflow progress
controller.record_success()
print(controller.get_progress())

# Save results
design.save_memory()
```

## Agent Types

### DesignAgent
Generates and analyzes drug candidate molecules
- Compound analysis and property prediction
- Molecule generation support
- Memory management with persistence
- 30+ methods for comprehensive analysis

### ADMETAgent  
Evaluates ADMET properties and filters candidates
- Drug-likeness prediction (Lipinski's Rule)
- Toxicity assessment
- Batch compound filtering
- Detailed property analysis

### ControllerAgent
Orchestrates multi-agent workflows
- Goal tracking and workflow management
- Progress monitoring and metrics
- Stopping criteria and iteration control
- Completion time estimation

## Features

✅ **Fast Initialization** - No heavy ML libraries loaded at startup  
✅ **Lazy Loading** - Tools load only when needed  
✅ **Memory System** - Persistent JSON storage with export/import  
✅ **Rich Analytics** - 65+ methods across all agents  
✅ **Workflow Oriented** - Built for drug discovery pipelines  
✅ **Well Documented** - 2000+ lines of API and usage docs  
✅ **Extensible** - Easy integration with external tools  

## Documentation

- **[AGENTS_API.md](../AGENTS_API.md)** - Complete API reference with examples
- **[AGENTS_QUICK_REFERENCE.py](../AGENTS_QUICK_REFERENCE.py)** - Quick lookup guide
- **[agents_examples.py](../agents_examples.py)** - 8 working examples

## File Structure

```
agents/
├── design_agent/
│   ├── agent.py          # DesignAgent implementation (250+ lines)
│   ├── memory.json       # Agent memory persistence
│   ├── goals.yaml        # Agent goals configuration
│   └── __init__.py
├── admet_agent/
│   ├── agent.py          # ADMETAgent implementation (180+ lines)
│   └── __init__.py
├── controller_agent/
│   ├── agent.py          # ControllerAgent implementation (130+ lines)
│   └── __init__.py
├── approval_agent.py
├── design_agent.py       # Backward compatibility wrapper
├── discovery_agent.py
├── multi_agent.py
├── validation_agent.py
└── __init__.py
```

## Method Overview

### DesignAgent (30+ methods)
```
Core Analysis:
  run()                    Analyze compound(s)
  generate_molecule()      Generate SMILES string
  _analyze_single()        Analyze single compound

Memory:
  load_memory()           Load from disk
  save_memory()           Save to disk
  export_memory()         Export to custom location
  import_memory()         Import from file

Statistics:
  get_stats()             Get basic statistics
  get_analysis_summary()  Get comprehensive summary
  get_successful_compounds()    Get all successes
  get_failed_compounds()        Get all failures
  get_top_successes()           Get top N compounds

Search & Filter:
  search_compound()       Find in history
  filter_by_status()      Filter by status

Logging:
  log_success()           Log successful compound
  log_failure()           Log failed compound

Utility:
  clear_memory()          Clear all memory
  print_summary()         Print formatted summary
```

### ADMETAgent (15+ methods)
```
Evaluation:
  evaluate()              Check ADMET pass/fail
  evaluate_with_details() Get detailed breakdown

Properties:
  get_admet_properties()  Get all properties
  predict_drug_likeness() Lipinski score
  predict_toxicity()      Toxicity prediction

Batch:
  batch_evaluate()        Evaluate multiple
  filter_compounds()      Filter library
  compare_compounds()     Compare multiple

Analytics:
  get_pass_rate()         Calculate pass rate
  get_evaluation_criteria() Get thresholds

Reporting:
  print_evaluation_report() Print formatted report
```

### ControllerAgent (20+ methods)
```
Stopping:
  stop()                  Check stop criteria
  should_continue()       Continue check

Tracking:
  record_success()        Log success
  record_failure()        Log failure
  next_iteration()        Move to next iteration

Progress:
  get_progress()          Get metrics
  get_success_rate()      Success percentage
  has_reached_target()    Target achieved?

Estimation:
  estimate_completion()   Est. remaining iterations
  get_remaining()         Get remaining counts

Goals:
  update_goals()          Update targets
  get_status()            Get current state
  reset()                 Reset to initial state

Reporting:
  log_milestone()         Log milestone
  print_progress()        Print formatted progress
```

## Usage Examples

### Single Compound Analysis
```python
from agents.design_agent.agent import DesignAgent

agent = DesignAgent()
result = agent.run("aspirin")
agent.log_success("aspirin", score=0.85)
agent.save_memory()
```

### Batch Analysis
```python
compounds = [
    {"cid": "5892", "iupac_name": "2-acetoxybenzoic acid"},
    {"cid": "3672", "iupac_name": "ibuprofen"},
]
result = agent.run(compounds_for_target=compounds)
agent.save_memory()
```

### Multi-Agent Workflow
```python
design = DesignAgent()
admet = ADMETAgent()
controller = ControllerAgent(goals={"target": 10})

while controller.should_continue(controller.iteration_count, controller.success_count):
    smiles = design.generate_molecule()
    if admet.evaluate(smiles):
        controller.record_success()
        design.log_success(smiles)
    else:
        controller.record_failure()
        design.log_failure(smiles, "ADMET veto")
    controller.next_iteration()

controller.print_progress()
design.save_memory()
```

### Compound Filtering
```python
admet = ADMETAgent()
smiles_list = ["CC(=O)Oc1ccccc1C(=O)O", ...]
result = admet.filter_compounds(smiles_list)
print(f"Passed: {result['pass_count']}/{result['total']}")
```

## Run Examples

All examples available in [agents_examples.py](../agents_examples.py):

```bash
python agents_examples.py 1  # Single compound analysis
python agents_examples.py 2  # Batch analysis
python agents_examples.py 3  # Multi-agent workflow
python agents_examples.py 4  # Compound filtering
python agents_examples.py 5  # Memory management
python agents_examples.py 6  # Progress tracking
python agents_examples.py 7  # Completion estimation
python agents_examples.py 8  # Evaluation reports
```

## Key Design Principles

1. **No Heavy Imports at Startup** - Fast initialization
2. **Lazy Loading** - Tools load on-demand
3. **Memory Persistence** - Auto-save and recovery
4. **Workflow-Oriented** - Built for pipelines
5. **Extensible** - Easy to integrate tools
6. **Well-Documented** - 2000+ lines of guides
7. **Production-Ready** - Complete error handling

## Memory Locations

- **DesignAgent**: `agents/design_agent/memory.json`
- **ADMETAgent**: `agents/admet_agent/memory.json`

Memory is automatically loaded on initialization and saved with `save_memory()`.

## Configuration

### DesignAgent
```python
agent = DesignAgent(use_tools=False)  # Disable tool loading for speed
```

### ADMETAgent
```python
agent = ADMETAgent(use_tools=False)   # Disable tool loading for speed
```

### ControllerAgent
```python
goals = {
    "target": 10,              # Target molecules
    "success_rate": 0.7,       # Success threshold
    "max_iterations": 100      # Max iterations
}
controller = ControllerAgent(goals=goals)
```

## Performance

- **Initialization**: ~instant (< 100ms)
- **Single Analysis**: depends on analysis method
- **Batch Analysis**: O(n) where n = number of compounds
- **Memory Save**: ~milliseconds
- **Memory Load**: ~milliseconds

## Integration

The agents can be easily integrated with:
- External property prediction tools
- Molecular docking engines
- QSAR models
- Generative models
- Database systems
- Web APIs

## Best Practices

✓ Initialize without tools for fast startup  
✓ Save memory periodically  
✓ Use batch_evaluate for multiple compounds  
✓ Check should_continue() in workflow loops  
✓ Log successes and failures for tracking  

✗ Don't load tools at initialization  
✗ Don't forget to save memory  
✗ Don't assume all analyses succeed  
✗ Don't use fixed iteration counts  
✗ Don't skip error handling  

## Support & Documentation

For detailed documentation, see:
- [AGENTS_API.md](../AGENTS_API.md) - Complete API reference
- [AGENTS_QUICK_REFERENCE.py](../AGENTS_QUICK_REFERENCE.py) - Quick lookup
- [agents_examples.py](../agents_examples.py) - Working examples
- [AGENTS_IMPLEMENTATION_SUMMARY.md](../AGENTS_IMPLEMENTATION_SUMMARY.md) - Overview

---

**Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: February 2026
