
from crewai import Agent, Task, Crew
try:
    from crewai.tools import BaseTool
except ImportError:
    BaseTool = object  # fallback if not found, will error with helpful message

from tools.pubmed import pubmed_search
from tools.pubchem import fetch_compound_data

class PubMedSearchTool(BaseTool):
    name: str = "PubMed Search"
    description: str = "Searches PubMed for articles."

    def _run(self, *args, **kwargs):
        return pubmed_search(*args, **kwargs)

class PubChemFetchTool(BaseTool):
    name: str = "PubChem Fetch"
    description: str = "Fetches compound data from PubChem."

    def _run(self, tool_input: dict):
        compound = tool_input.get("compound")
        return fetch_compound_data(compound)

def create_drug_discovery_crew():
    researcher = Agent(
        role="Biomedical Researcher",
        goal="Find relevant drug studies",
        backstory="Expert in literature analysis",
        tools=[PubMedSearchTool()],
        verbose=True
    )

    chemist = Agent(
        role="Medicinal Chemist",
        goal="Analyze compound properties",
        backstory="Computational chemistry specialist",
        tools=[PubChemFetchTool()],
        verbose=True
    )

    literature_review = Task(
        description="Find studies on Alzheimer's drug candidates",
        agent=researcher,
        expected_output="A list of relevant studies on Alzheimer's drug candidates."
    )

    compound_analysis = Task(
        description="Analyze chemical properties of {compound} and assess its drug potential.",
        agent=chemist,
        context=[literature_review],
        expected_output="A summary of chemical properties for each candidate."
    )

    return Crew(agents=[researcher, chemist], tasks=[literature_review, compound_analysis])
