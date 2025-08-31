

import streamlit as st
import requests
import re

st.title("Drug Discovery AI Assistant")
query = st.text_input("Enter disease, target, or compound:")

def extract_alphafold_url(structure_msg):
    match = re.search(r"https://alphafold.ebi.ac.uk/entry/[^\s]+", structure_msg)
    return match.group(0) if match else None

def is_pdb_content(text):
    # Simple check for PDB file content
    return text and text.startswith("HEADER") and "ATOM" in text

if st.button("Submit"):
    if query:
        try:
            response = requests.get(f"http://127.0.0.1:8000/full_workflow?query={query}")
            if response.status_code == 200:
                result = response.json()
                structure_msg = None
                if isinstance(result, dict) and "discovery" in result and isinstance(result["discovery"], dict):
                    structure_msg = result["discovery"].get("structure", "")
                elif isinstance(result, dict) and "structure" in result:
                    structure_msg = result.get("structure", "")
                else:
                    structure_msg = None

                if structure_msg:
                    if is_pdb_content(structure_msg):
                        st.success("AlphaFold structure found and downloaded automatically.")
                        st.download_button(
                            label="Download AlphaFold PDB",
                            data=structure_msg,
                            file_name=f"{query}.pdb",
                            mime="chemical/x-pdb"
                        )
                    else:
                        download_url = extract_alphafold_url(structure_msg)
                        if download_url:
                            st.warning("AlphaFold structure not found online for this query.")
                            st.markdown(f"[Click here to download from AlphaFold]({download_url})")
                        else:
                            st.info(structure_msg)
                st.json(result)
            else:
                st.error(f"API error: {response.status_code}")
        except Exception as e:
            st.error(f"Request failed: {e}")
    else:
        st.warning("Please enter a query.")
