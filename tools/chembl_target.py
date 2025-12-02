import requests

def get_chembl_compounds_for_target(target, max_results=5):
    """
    Query ChEMBL for compounds known to interact with a given target (gene/protein name).
    Returns a list of dictionaries with ChEMBL ID and preferred name.
    """
    # Step 1: Find ChEMBL target ID by gene/protein name
    search_url = f"https://www.ebi.ac.uk/chembl/api/data/target/search?q={target}&format=json"
    try:
        resp = requests.get(search_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data["page_meta"]["total_count"] == 0:
            return []
        chembl_target_id = data["targets"][0]["target_chembl_id"]
        # Step 2: Find activities (compounds) for this target
        act_url = f"https://www.ebi.ac.uk/chembl/api/data/activity?target_chembl_id={chembl_target_id}&limit={max_results}&format=json"
        act_resp = requests.get(act_url, timeout=10)
        act_resp.raise_for_status()
        act_data = act_resp.json()
        compounds = []
        for act in act_data.get("activities", []):
            mol_chembl_id = act.get("molecule_chembl_id")
            # Optionally, get molecule preferred name
            mol_url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{mol_chembl_id}.json"
            mol_resp = requests.get(mol_url, timeout=10)
            if mol_resp.status_code == 200:
                mol_data = mol_resp.json()
                pref_name = mol_data.get("pref_name", "")
            else:
                pref_name = ""
            compounds.append({"chembl_id": mol_chembl_id, "pref_name": pref_name})
        return compounds
    except Exception as e:
        return [{"error": f"ChEMBL API error: {e}"}]
