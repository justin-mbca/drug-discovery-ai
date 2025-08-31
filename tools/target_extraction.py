import requests
from collections import Counter
import re

# Helper to fetch PubMed abstracts for a list of PMIDs

def fetch_pubmed_abstracts(pmids, retmax=3):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "text",
        "rettype": "abstract"
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return ""

# Simple protein/gene name extraction (NER can be added later)
def extract_targets_from_abstracts(abstracts, top_n=5):
    # Regex for common protein/gene name patterns (very basic)
    matches = re.findall(r'\b[A-Z0-9]{2,10}\b', abstracts)
    # Remove common English words and numbers
    blacklist = set(["AND", "THE", "FOR", "WITH", "FROM", "THIS", "THAT", "WAS", "ARE", "HAVE", "HAS", "WERE", "NOT", "BUT", "ALL", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN"])
    filtered = [m for m in matches if not m.isdigit() and m not in blacklist and len(m) > 2]
    counter = Counter(filtered)
    return [name for name, _ in counter.most_common(top_n)]
