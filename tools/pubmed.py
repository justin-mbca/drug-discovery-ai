
import requests

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