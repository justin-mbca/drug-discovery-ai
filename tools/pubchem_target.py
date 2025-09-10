import requests

def get_compounds_for_target(target, max_results=5):
    """
    Query PubChem for compounds known to interact with a given protein/gene target.
    Returns a list of compound names/IDs.
    Fallback: If gene/assay endpoint fails, try compound name search for CIDs.
    """
    # First try the gene/assay endpoint
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/target/gene/{target}/aids/JSON"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        aids = data.get("InformationList", {}).get("Information", [{}])[0].get("AID", [])
        compounds = set()
        for aid in aids[:max_results]:
            assay_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/cids/JSON"
            assay_resp = requests.get(assay_url, timeout=10)
            if assay_resp.status_code == 200:
                assay_data = assay_resp.json()
                cids = assay_data.get("InformationList", {}).get("Information", [{}])[0].get("CID", [])
                compounds.update(cids[:max_results])
        compound_names = []
        for cid in list(compounds)[:max_results]:
            name_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IUPACName/JSON"
            name_resp = requests.get(name_url, timeout=10)
            if name_resp.status_code == 200:
                name_data = name_resp.json()
                props = name_data.get("PropertyTable", {}).get("Properties", [{}])[0]
                compound_names.append({"cid": cid, "iupac_name": props.get("IUPACName", "")})
            else:
                compound_names.append({"cid": cid, "iupac_name": ""})
        # Fallback if no compounds found
        if not compound_names:
            # Try compound name search for CIDs
            fallback_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{target}/cids/JSON"
            fallback_resp = requests.get(fallback_url, timeout=10)
            if fallback_resp.status_code == 200:
                fallback_data = fallback_resp.json()
                cids = fallback_data.get("IdentifierList", {}).get("CID", [])
                fallback_compounds = []
                for cid in cids[:max_results]:
                    name_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IUPACName/JSON"
                    name_resp = requests.get(name_url, timeout=10)
                    if name_resp.status_code == 200:
                        name_data = name_resp.json()
                        props = name_data.get("PropertyTable", {}).get("Properties", [{}])[0]
                        fallback_compounds.append({"cid": cid, "iupac_name": props.get("IUPACName", "")})
                    else:
                        fallback_compounds.append({"cid": cid, "iupac_name": ""})
                if fallback_compounds:
                    return fallback_compounds
        return compound_names
    except Exception as e:
        # Fallback: try compound name search for CIDs if first endpoint fails
        try:
            fallback_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{target}/cids/JSON"
            fallback_resp = requests.get(fallback_url, timeout=10)
            if fallback_resp.status_code == 200:
                fallback_data = fallback_resp.json()
                cids = fallback_data.get("IdentifierList", {}).get("CID", [])
                fallback_compounds = []
                for cid in cids[:max_results]:
                    name_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IUPACName/JSON"
                    name_resp = requests.get(name_url, timeout=10)
                    if name_resp.status_code == 200:
                        name_data = name_resp.json()
                        props = name_data.get("PropertyTable", {}).get("Properties", [{}])[0]
                        fallback_compounds.append({"cid": cid, "iupac_name": props.get("IUPACName", "")})
                    else:
                        fallback_compounds.append({"cid": cid, "iupac_name": ""})
                if fallback_compounds:
                    return fallback_compounds
            return [{"error": f"PubChem API error: {e}"}]
        except Exception as e2:
            return [{"error": f"PubChem API error: {e2}"}]
