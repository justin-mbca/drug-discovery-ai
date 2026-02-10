"""
LangGraph-Based Drug Discovery Agent System with Reasoning

This module implements a graph-based multi-agent workflow using LangGraph,
featuring ReAct reasoning patterns, conditional routing, and state persistence.
"""

from typing import Annotated, TypedDict, List, Dict, Optional, Literal
from typing_extensions import TypedDict
import operator
from datetime import datetime
import json
import os

# LangGraph imports (will be lazy-loaded to maintain fast startup)
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None
    MemorySaver = None
    BaseMessage = None
    HumanMessage = None
    AIMessage = None
    SystemMessage = None


# =============================================================================
# STATE SCHEMA
# =============================================================================

class AgentState(TypedDict):
    """
    State schema for the drug discovery workflow
    
    This state is passed between nodes in the graph and tracks:
    - Current compound being analyzed
    - Messages and reasoning traces
    - Agent results and decisions
    - Iteration tracking
    - Success/failure history
    """
    # Input
    compound: str
    smiles: Optional[str]
    
    # Messages (reasoning traces)
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Agent results
    design_result: Optional[Dict]
    admet_result: Optional[Dict]
    validation_result: Optional[Dict]
    
    # Decision tracking
    current_step: str
    next_action: str
    reasoning: str
    
    # Workflow control
    iteration: int
    success_count: int
    failure_count: int
    max_iterations: int
    target_successes: int
    
    # History
    successful_compounds: List[Dict]
    failed_compounds: List[Dict]
    
    # Final output
    final_decision: Optional[str]
    confidence_score: Optional[float]


# =============================================================================
# REASONING PATTERNS
# =============================================================================

class ReActReasoning:
    """
    ReAct (Reasoning + Acting) pattern implementation
    
    Combines reasoning traces with action execution for transparent decision-making.
    Each step includes: Thought -> Action -> Observation -> Reflection
    """
    
    @staticmethod
    def thought(state: AgentState, thought_text: str) -> Dict:
        """Record a reasoning thought"""
        message = AIMessage(content=f"💭 THOUGHT: {thought_text}")
        return {
            "messages": [message],
            "reasoning": thought_text
        }
    
    @staticmethod
    def action(state: AgentState, action_name: str, action_params: Dict) -> Dict:
        """Record an action being taken"""
        message = AIMessage(content=f"🎯 ACTION: {action_name} with params {action_params}")
        return {
            "messages": [message],
            "next_action": action_name
        }
    
    @staticmethod
    def observation(state: AgentState, observation_text: str) -> Dict:
        """Record observation from action"""
        message = AIMessage(content=f"👁️ OBSERVATION: {observation_text}")
        return {
            "messages": [message]
        }
    
    @staticmethod
    def reflection(state: AgentState, reflection_text: str) -> Dict:
        """Reflect on results and decide next step"""
        message = AIMessage(content=f"🤔 REFLECTION: {reflection_text}")
        return {
            "messages": [message],
            "reasoning": reflection_text
        }


# =============================================================================
# GRAPH NODES (AGENT FUNCTIONS)
# =============================================================================

def initialize_workflow(state: AgentState) -> AgentState:
    """Initialize the workflow with input validation and setup"""
    compound = state.get("compound", "")
    
    # Add system message
    system_msg = SystemMessage(
        content="Drug Discovery AI Agent - Analyzing compounds using ReAct reasoning"
    )
    
    # Add initialization message
    init_msg = HumanMessage(content=f"Analyze compound: {compound}")
    
    # Reasoning: What should I do first?
    thought = ReActReasoning.thought(
        state,
        f"I need to analyze {compound}. First, I'll design and evaluate its properties."
    )
    
    return {
        **state,
        "messages": [system_msg, init_msg] + thought["messages"],
        "current_step": "initialized",
        "next_action": "design",
        "reasoning": thought["reasoning"],
        "iteration": state.get("iteration", 0) + 1
    }


def design_agent_node(state: AgentState) -> AgentState:
    """
    Design Agent Node - Analyzes compound structure and properties
    
    Uses ReAct reasoning to:
    1. Think about what properties to evaluate
    2. Act by analyzing the compound
    3. Observe the results
    4. Reflect on whether to proceed
    """
    from agents.design_agent.agent import DesignAgent
    
    compound = state["compound"]
    
    # THOUGHT: Plan the analysis
    thought_update = ReActReasoning.thought(
        state,
        f"Analyzing {compound}. I'll check molecular properties and drug-likeness."
    )
    
    # ACTION: Run design agent
    action_update = ReActReasoning.action(
        state,
        "design_agent.run",
        {"compound": compound}
    )
    
    # Execute action
    agent = DesignAgent(use_tools=False)
    result = agent.run(compound)
    
    # OBSERVATION: Capture results
    observation_text = f"Design analysis complete. Status: {result.get('status', 'unknown')}"
    observation_update = ReActReasoning.observation(state, observation_text)
    
    # REFLECTION: Decide next step
    if result.get("status") == "completed":
        reflection_text = "Design looks promising. Proceeding to ADMET evaluation."
        next_action = "admet"
    else:
        reflection_text = "Design analysis inconclusive. May need alternative compound."
        next_action = "validate"
    
    reflection_update = ReActReasoning.reflection(state, reflection_text)
    
    return {
        **state,
        "messages": state["messages"] + thought_update["messages"] + action_update["messages"] + 
                   observation_update["messages"] + reflection_update["messages"],
        "design_result": result,
        "current_step": "design",
        "next_action": next_action,
        "reasoning": reflection_update["reasoning"]
    }


def admet_agent_node(state: AgentState) -> AgentState:
    """
    ADMET Agent Node - Evaluates drug-likeness and ADMET properties
    
    Uses ReAct reasoning for transparent ADMET evaluation
    """
    from agents.admet_agent.agent import ADMETAgent
    
    compound = state["compound"]
    smiles = state.get("smiles", "CC(=O)Oc1ccccc1C(=O)O")  # Default to aspirin
    
    # THOUGHT
    thought_update = ReActReasoning.thought(
        state,
        f"Evaluating ADMET properties for {compound}. Checking drug-likeness and toxicity."
    )
    
    # ACTION
    action_update = ReActReasoning.action(
        state,
        "admet_agent.evaluate",
        {"smiles": smiles}
    )
    
    # Execute
    agent = ADMETAgent(use_tools=False)
    passes = agent.evaluate(smiles)
    properties = agent.get_admet_properties(smiles)
    
    # OBSERVATION
    observation_text = f"ADMET evaluation: {'PASS' if passes else 'FAIL'}. Properties: {properties}"
    observation_update = ReActReasoning.observation(state, observation_text)
    
    # REFLECTION
    if passes:
        reflection_text = "ADMET properties acceptable. Compound is viable for further validation."
        next_action = "validate"
        state["success_count"] = state.get("success_count", 0) + 1
    else:
        reflection_text = "ADMET properties inadequate. Compound rejected."
        next_action = "decide"
        state["failure_count"] = state.get("failure_count", 0) + 1
    
    reflection_update = ReActReasoning.reflection(state, reflection_text)
    
    result = {
        "passes": passes,
        "properties": properties,
        "timestamp": datetime.now().isoformat()
    }
    
    return {
        **state,
        "messages": state["messages"] + thought_update["messages"] + action_update["messages"] + 
                   observation_update["messages"] + reflection_update["messages"],
        "admet_result": result,
        "current_step": "admet",
        "next_action": next_action,
        "reasoning": reflection_update["reasoning"]
    }


def validation_node(state: AgentState) -> AgentState:
    """
    Validation Node - Final validation and scoring
    
    Combines all results and makes final decision
    """
    compound = state["compound"]
    
    # THOUGHT
    thought_update = ReActReasoning.thought(
        state,
        f"Validating all results for {compound}. Combining design and ADMET outcomes."
    )
    
    # ACTION
    action_update = ReActReasoning.action(
        state,
        "validate_compound",
        {"design": state.get("design_result"), "admet": state.get("admet_result")}
    )
    
    # Combine results
    design_ok = state.get("design_result", {}).get("status") == "completed"
    admet_ok = state.get("admet_result", {}).get("passes", False)
    
    validation_result = {
        "compound": compound,
        "design_passed": design_ok,
        "admet_passed": admet_ok,
        "overall_pass": design_ok and admet_ok,
        "timestamp": datetime.now().isoformat()
    }
    
    # OBSERVATION
    observation_text = f"Validation complete. Overall: {'PASS' if validation_result['overall_pass'] else 'FAIL'}"
    observation_update = ReActReasoning.observation(state, observation_text)
    
    # REFLECTION
    if validation_result['overall_pass']:
        reflection_text = f"✅ {compound} validated successfully! Adding to successful compounds."
        state["successful_compounds"] = state.get("successful_compounds", []) + [validation_result]
        final_decision = "APPROVED"
        confidence = 0.9
    else:
        reflection_text = f"❌ {compound} failed validation. Recording failure."
        state["failed_compounds"] = state.get("failed_compounds", []) + [validation_result]
        final_decision = "REJECTED"
        confidence = 0.8
    
    reflection_update = ReActReasoning.reflection(state, reflection_text)
    
    return {
        **state,
        "messages": state["messages"] + thought_update["messages"] + action_update["messages"] + 
                   observation_update["messages"] + reflection_update["messages"],
        "validation_result": validation_result,
        "current_step": "validation",
        "next_action": "decide",
        "reasoning": reflection_update["reasoning"],
        "final_decision": final_decision,
        "confidence_score": confidence
    }


def decision_node(state: AgentState) -> AgentState:
    """
    Decision Node - Decides whether to continue or terminate workflow
    
    Uses ReAct reasoning to determine if more iterations are needed
    """
    iteration = state.get("iteration", 0)
    success_count = state.get("success_count", 0)
    max_iterations = state.get("max_iterations", 10)
    target_successes = state.get("target_successes", 5)
    
    # THOUGHT
    thought_text = f"Current status: {success_count}/{target_successes} successes, iteration {iteration}/{max_iterations}"
    thought_update = ReActReasoning.thought(state, thought_text)
    
    # REFLECTION
    if success_count >= target_successes:
        reflection_text = f"🎉 Target reached! Found {success_count} successful compounds."
        next_action = "end"
    elif iteration >= max_iterations:
        reflection_text = f"⏱️ Max iterations reached. Found {success_count} compounds."
        next_action = "end"
    else:
        reflection_text = f"🔄 Continuing search. Need {target_successes - success_count} more."
        next_action = "continue"
    
    reflection_update = ReActReasoning.reflection(state, reflection_text)
    
    return {
        **state,
        "messages": state["messages"] + thought_update["messages"] + reflection_update["messages"],
        "current_step": "decision",
        "next_action": next_action,
        "reasoning": reflection_update["reasoning"]
    }


# =============================================================================
# CONDITIONAL EDGES (ROUTING LOGIC)
# =============================================================================

def route_after_decision(state: AgentState) -> str:
    """Route based on decision node outcome"""
    next_action = state.get("next_action", "end")
    if next_action == "continue":
        return "initialize"
    return END


def route_after_design(state: AgentState) -> str:
    """Route based on design results"""
    next_action = state.get("next_action", "admet")
    return next_action


def route_after_admet(state: AgentState) -> str:
    """Route based on ADMET results"""
    next_action = state.get("next_action", "validate")
    return next_action


# =============================================================================
# GRAPH BUILDER
# =============================================================================

def create_drug_discovery_graph():
    """
    Create the LangGraph state graph for drug discovery workflow
    
    Returns:
        Compiled graph with checkpointing enabled
    """
    if not LANGGRAPH_AVAILABLE:
        raise ImportError(
            "LangGraph not available. Install with: pip install langgraph langchain-core"
        )
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_workflow)
    workflow.add_node("design", design_agent_node)
    workflow.add_node("admet", admet_agent_node)
    workflow.add_node("validate", validation_node)
    workflow.add_node("decide", decision_node)
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    # Add edges
    workflow.add_edge("initialize", "design")
    workflow.add_conditional_edges("design", route_after_design)
    workflow.add_conditional_edges("admet", route_after_admet)
    workflow.add_edge("validate", "decide")
    workflow.add_conditional_edges("decide", route_after_decision)
    
    # Compile with checkpointing
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)
    
    return graph


# =============================================================================
# HIGH-LEVEL API
# =============================================================================

class LangGraphDrugDiscoveryAgent:
    """
    High-level API for LangGraph-based drug discovery
    
    Features:
    - ReAct reasoning patterns
    - Stateful workflow with checkpointing
    - Conditional routing based on results
    - Transparent decision traces
    """
    
    def __init__(self, max_iterations: int = 10, target_successes: int = 5):
        """Initialize the LangGraph agent"""
        if not LANGGRAPH_AVAILABLE:
            raise ImportError(
                "LangGraph not available. Install with: pip install langgraph langchain-core"
            )
        
        self.graph = create_drug_discovery_graph()
        self.max_iterations = max_iterations
        self.target_successes = target_successes
        self.thread_id = f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def analyze_compound(self, compound: str, smiles: Optional[str] = None) -> Dict:
        """
        Analyze a single compound using LangGraph workflow
        
        Args:
            compound: Compound name
            smiles: Optional SMILES string
            
        Returns:
            Final state with reasoning traces
        """
        # Initial state
        initial_state = {
            "compound": compound,
            "smiles": smiles,
            "messages": [],
            "design_result": None,
            "admet_result": None,
            "validation_result": None,
            "current_step": "start",
            "next_action": "design",
            "reasoning": "",
            "iteration": 0,
            "success_count": 0,
            "failure_count": 0,
            "max_iterations": self.max_iterations,
            "target_successes": self.target_successes,
            "successful_compounds": [],
            "failed_compounds": [],
            "final_decision": None,
            "confidence_score": None
        }
        
        # Run graph
        config = {"configurable": {"thread_id": self.thread_id}}
        final_state = None
        
        for state in self.graph.stream(initial_state, config):
            final_state = state
        
        return final_state
    
    def get_reasoning_trace(self, state: Dict) -> List[str]:
        """Extract reasoning trace from state messages"""
        if not state:
            return []
        
        messages = []
        for node_state in state.values():
            if isinstance(node_state, dict) and "messages" in node_state:
                for msg in node_state["messages"]:
                    if hasattr(msg, "content"):
                        messages.append(msg.content)
        
        return messages
    
    def export_results(self, state: Dict, filepath: str):
        """Export results to JSON file"""
        if not state:
            return
        
        # Get the last node's state
        final_node_state = list(state.values())[-1] if state else {}
        
        export_data = {
            "compound": final_node_state.get("compound"),
            "final_decision": final_node_state.get("final_decision"),
            "confidence_score": final_node_state.get("confidence_score"),
            "iteration": final_node_state.get("iteration"),
            "success_count": final_node_state.get("success_count"),
            "failure_count": final_node_state.get("failure_count"),
            "design_result": final_node_state.get("design_result"),
            "admet_result": final_node_state.get("admet_result"),
            "validation_result": final_node_state.get("validation_result"),
            "reasoning_trace": self.get_reasoning_trace(state),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filepath


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("LangGraph Drug Discovery Agent - ReAct Reasoning Demo")
    print("=" * 70)
    
    if not LANGGRAPH_AVAILABLE:
        print("\n❌ LangGraph not installed!")
        print("Install with: pip install langgraph langchain-core langchain-openai")
        exit(1)
    
    # Create agent
    agent = LangGraphDrugDiscoveryAgent(max_iterations=3, target_successes=1)
    
    # Analyze compound
    print("\n🔬 Analyzing compound: aspirin\n")
    result = agent.analyze_compound("aspirin", smiles="CC(=O)Oc1ccccc1C(=O)O")
    
    # Display reasoning trace
    print("\n" + "=" * 70)
    print("REASONING TRACE")
    print("=" * 70)
    
    reasoning_trace = agent.get_reasoning_trace(result)
    for i, trace in enumerate(reasoning_trace, 1):
        print(f"{i}. {trace}")
    
    # Display final results
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    
    if result:
        final_state = list(result.values())[-1]
        print(f"Compound: {final_state.get('compound')}")
        print(f"Decision: {final_state.get('final_decision')}")
        print(f"Confidence: {final_state.get('confidence_score')}")
        print(f"Iterations: {final_state.get('iteration')}")
        
        # Export results
        export_path = "/tmp/langgraph_drug_discovery_results.json"
        agent.export_results(result, export_path)
        print(f"\n✅ Results exported to: {export_path}")
