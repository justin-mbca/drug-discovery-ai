
def pubmed_search(query: str) -> str:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 3
    }
    response = requests.get(base_url, params=params)
    return response.json()


# Add PubMedTool class for agent compatibility

import requests

class PubMedTool:
    def search(self, query, retmax=3):
        """
        Search PubMed for the query and return a list of PubMed IDs (PMIDs).
        """
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