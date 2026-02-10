import requests
from crewai.tools.base_tool import BaseTool

class PubMedTool(BaseTool):
    name: str = "PubMed Search"
    description: str = "Search PubMed for studies related to a compound. Returns a list of PubMed IDs."

    def _run(self, query: str, retmax: int = 3):
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": retmax
        }
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            pmids = data.get("esearchresult", {}).get("idlist", [])
            return pmids
        except requests.RequestException as e:
            return [f"PubMed API error: {e}"]