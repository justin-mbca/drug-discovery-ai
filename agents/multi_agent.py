
from crewai import Agent, Task, Crew
from tools.pubmed import PubMedTool
from tools.pubchem import PubChemTool

def create_drug_discovery_crew():
    pubmed_tool = PubMedTool()
    pubchem_tool = PubChemTool()

    researcher = Agent(
        role="Biomedical Researcher",
        goal="Find relevant drug studies",
        backstory="Expert in literature analysis",
        tools=[pubmed_tool],
        verbose=True
    )

    chemist = Agent(
        role="Medicinal Chemist",
        goal="Analyze compound properties",
        backstory="Computational chemistry specialist",
        tools=[pubchem_tool],
        verbose=True
    )

    literature_review = Task(
        description="Find studies on {compound} as a potential Alzheimer's drug candidate.",
        agent=researcher,
        expected_output="A list of relevant PubMed IDs and a summary of key findings from the literature."
    )

    compound_analysis = Task(
        description="Analyze chemical properties of {compound} and assess its drug potential.",
        agent=chemist,
        context=[literature_review],
        expected_output="A summary of chemical properties for each candidate."
    )
    
    return Crew(agents=[researcher, chemist], tasks=[literature_review, compound_analysis])
