
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
class PubMedTool:
    def search(self, query):
        # Stub: Replace with real PubMed API call or use pubmed_search
        return [f"Mock PubMed result for {query}"]