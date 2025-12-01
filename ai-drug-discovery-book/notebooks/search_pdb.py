# src/search_all_als_pdbs.py

import requests
import time

# List of 26 ALS-related genes
als_genes = [
    "SOD1","FUS","TARDBP","C9orf72","UBQLN2","OPTN","VCP","ANG",
    "SETX","PFN1","CHCHD10","TBK1","NEK1","MATR3","TIA1","HNRNPA1",
    "HNRNPA2B1","ALS2","DAO","FIG4","SPG11","ATXN2","GRN","SQSTM1",
    "SIGMAR1","DCTN1","KIF5A"
]

# RCSB PDB search API
url = "https://search.rcsb.org/rcsbsearch/v1/query"

pdb_ids = set()  # Use a set to avoid duplicates

for gene in als_genes:
    query_json = {
        "query": {
            "type": "terminal",
            "service": "full_text",
            "parameters": {"value": gene}
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {"start":0,"rows":100},
            "results_content_type": ["experimental"],
            "sort": [{"sort_by":"resolution","direction":"asc"}]
        }
    }

    try:
        response = requests.post(url, json=query_json)
        data = response.json()
        results = data.get("result_set", [])
        for r in results:
            pdb_ids.add(r["identifier"])
        print(f"{gene}: found {len(results)} PDB entries")
    except Exception as e:
        print(f"{gene}: error {e}")

    time.sleep(0.2)  # polite delay to avoid hammering API

print("\n=== Summary ===")
print(f"Total unique PDB entries found: {len(pdb_ids)}")
print("PDB IDs:", sorted(pdb_ids))
