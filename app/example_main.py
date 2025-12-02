from fastapi import FastAPI
from agents.discovery_agent import DiscoveryAgent
from agents.design_agent import DesignAgent
from agents.validation_agent import ValidationAgent
from agents.approval_agent import ApprovalAgent

discovery_agent = DiscoveryAgent()
design_agent = DesignAgent()
validation_agent = ValidationAgent()
approval_agent = ApprovalAgent()
app = FastAPI()


# app/example_main.py
from fastapi import FastAPI
from agents.discovery_agent import DiscoveryAgent
from agents.design_agent import DesignAgent
from agents.validation_agent import ValidationAgent
from agents.approval_agent import ApprovalAgent

discovery_agent = DiscoveryAgent()
design_agent = DesignAgent()
validation_agent = ValidationAgent()
approval_agent = ApprovalAgent()
app = FastAPI()

@app.get("/discovery")
def discovery(query: str):
    """Test DiscoveryAgent with a query (e.g., target name)"""
    return discovery_agent.run(query)

@app.get("/design")
def design(compound: str):
    """Test DesignAgent with a compound name"""
    return design_agent.run(compound)

@app.get("/validation")
def validation(candidate: str):
    """Test ValidationAgent with a candidate drug name"""
    return validation_agent.run(candidate)

@app.get("/approval")
def approval(candidate: str):
    """Test ApprovalAgent with a candidate drug name"""
    return approval_agent.run(candidate)


@app.get("/full_workflow")
def full_workflow(query: str):
    """Run the full drug discovery workflow: Discovery -> Design -> Validation -> Approval"""
    # Discovery stage
    discovery_result = discovery_agent.run(query)
    # If compounds_for_target is present, use it for design agent
    compounds_for_target = discovery_result.get("compounds_for_target")
    compound = query  # fallback
    # Design stage
    design_result = design_agent.run(compound, compounds_for_target=compounds_for_target)
    # Validation and approval use the original query (or could be extended to use top compound)
    validation_result = validation_agent.run(compound)
    approval_result = approval_agent.run(compound)
    return {
        "discovery": discovery_result,
        "design": design_result,
        "validation": validation_result,
        "approval": approval_result
    }
