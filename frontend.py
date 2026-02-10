
import streamlit as st
import requests
import re

# Disease to protein mapping for AlphaFold queries (symbol, UniProt ID)
disease_to_protein = {
    "Alzheimer's disease": [
        ("APP", "P05067"),
        ("MAPT", "P10636"),
        ("PSEN1", "P49768"),
        ("BACE1", "P56817")
    ],
    "Parkinson's disease": [
        ("SNCA", "P37840"),
        ("LRRK2", "Q5S007"),
        ("PARK7", "Q99497"),
        ("PINK1", "Q9BXM7")
    ],
    "Amyotrophic lateral sclerosis (ALS)": [
        ("SOD1", "P00441"),
        ("C9orf72", "O14776"),
        ("FUS", "P35637"),
        ("TARDBP", "Q13148")
    ],
    "Pancreatic cancer": [
        ("KRAS", "P01116"),
        ("TP53", "P04637"),
        ("CDKN2A", "P42771"),
        ("SMAD4", "Q13485")
    ],
    "Breast cancer": [
        ("BRCA1", "P38398"),
        ("BRCA2", "P51587"),
        ("ESR1", "P03372"),
        ("HER2", "P04626")
    ],
    "Lung cancer": [
        ("EGFR", "P00533"),
        ("ALK", "Q9UM73"),
        ("KRAS", "P01116"),
        ("TP53", "P04637")
    ],
    "Diabetes mellitus": [
        ("INS", "P01308"),
        ("GCK", "P35557"),
        ("HNF1A", "P20823"),
        ("PPARG", "P37231")
    ],
    "COVID-19": [
        ("ACE2", "Q9BYF1"),
        ("TMPRSS2", "O15393")
        # S and N are viral proteins, not in UniProt human
    ],
    "Rheumatoid arthritis": [
        ("TNF", "P01375"),
        ("IL6", "P05231"),
        ("PTPN22", "Q9Y2R2"),
        ("STAT4", "Q14765")
    ],
    "Multiple sclerosis": [
        ("HLA-DRB1", "P04229"),
        ("IL2RA", "P60568"),
        ("IL7R", "P16871"),
        ("CD6", "P30203")
    ],
    "Huntington's disease": [
        ("HTT", "P42858")
    ],
    "Ovarian cancer": [
        ("BRCA1", "P38398"),
        ("BRCA2", "P51587"),
        ("TP53", "P04637"),
        ("PTEN", "P60484")
    ],
    "Glioblastoma": [
        ("EGFR", "P00533"),
        ("PTEN", "P60484"),
        ("TP53", "P04637"),
        ("IDH1", "O75874")
    ],
    "Leukemia": [
        ("BCR", "P11274"),
        ("ABL1", "P00519"),
        ("FLT3", "P36888"),
        ("NPM1", "P06748")
    ],
    "Prostate cancer": [
        ("AR", "P10275"),
        ("TP53", "P04637"),
        ("PTEN", "P60484"),
        ("NKX3-1", "Q99801")
    ]
}


st.title("Drug Discovery AI Assistant")

# Information about PubChem and ChEMBL
with st.expander("ℹ️ About PubChem and ChEMBL", expanded=True):
    st.markdown("""
**PubChem** is a free chemistry database maintained by the NIH, providing information on the biological activities of small molecules. When you search for compounds by target, PubChem returns compounds that have been experimentally tested against the selected protein or gene.

**ChEMBL** is a manually curated database of bioactive molecules with drug-like properties, maintained by EMBL-EBI. ChEMBL provides compounds and their activities against biological targets, often including more curated and literature-derived data than PubChem.

**How are they linked?**
- PubChem and ChEMBL are separate databases. The same compound may appear in both, but with different IDs (PubChem CID vs. ChEMBL ID).
- In this app, you can select compounds from either source for further analysis. If you want to cross-reference a compound, you can search for its name or structure (SMILES) in the other database.
    """)

# User guidance for workflow steps
with st.expander("🧭 How to Use This App (Step-by-Step Guide)", expanded=True):
    st.markdown("""
**1. Disease-Driven Discovery**
   - Select or enter a disease of interest.
   - The app will suggest protein/gene targets and show links to AlphaFold structures.
   - Select a target to proceed to target-driven discovery.

**2. Target-Driven Discovery**
   - Enter or select a protein/gene target (e.g., BACE1, TP53).
   - The app will search PubChem and ChEMBL for compounds known to interact with this target.
   - Review the suggested compounds from both sources.
   - Select a compound from either PubChem or ChEMBL to proceed to compound-driven discovery.

**3. Compound-Driven Discovery**
   - Enter or select a compound (name, SMILES, or ID).
   - The app will analyze the compound’s properties and suggest possible new uses or effects.

**Tips:**
- PubChem and ChEMBL results are independent; you can use compounds from either for the next step.
- If no compounds are found in one database, try the other or select a different target.
    """)

# Step 1: Select entry type

# Step 2: Show relevant input and steps

# Step 3: Show procedure steps
def extract_alphafold_url(structure_message):
    match = re.search(r"https://alphafold.ebi.ac.uk/entry/[^\s]+", structure_message)
    return match.group(0) if match else None

def is_pdb_content(text):
    # Simple check for PDB file content
    return text and text.startswith("HEADER") and "ATOM" in text

disease_list = [
    "Alzheimer's disease",
    "Parkinson's disease",
    "Amyotrophic lateral sclerosis (ALS)",
    "Pancreatic cancer",
    "Breast cancer",
    "Lung cancer",
    "Diabetes mellitus",
    "COVID-19",
    "Rheumatoid arthritis",
    "Multiple sclerosis",
    "Huntington's disease",
    "Ovarian cancer",
    "Glioblastoma",
    "Leukemia",
    "Prostate cancer"
]
st.header("1. Disease-Driven Discovery")
col1, col2 = st.columns([2, 3])
with col1:
    selected_disease = st.selectbox(
        "Select a current research disease:",
        ["(Choose a disease)"] + disease_list,
        key="disease_select_box"
    )
with col2:
    disease_input = st.text_input(
        "Or enter a disease name (e.g., Alzheimer's disease, pancreatic cancer)",
        value=st.session_state.get("disease_input", ""),
        placeholder="Alzheimer's disease"
    )
# If a disease is selected from the dropdown, auto-fill the input box
if selected_disease and selected_disease != "(Choose a disease)":
    st.session_state["disease_input"] = selected_disease
    disease_input = selected_disease
suggested_targets = None
disease_steps = [
    "Identify key biological targets involved in the disease.",
    "Search for compounds that interact with these targets.",
    "Evaluate and optimize compounds for efficacy and safety."
]
st.markdown("**Procedure Steps:**")
for i, step in enumerate(disease_steps, 1):
    st.markdown(f"**Step {i}:** {step}")

# Target Section
st.header("2. Target-Driven Discovery")
target_input = st.text_input(
    "Enter a target (protein/gene) name (e.g., BACE1, APP, MAPT)",
    value=st.session_state.get("target_input", ""),
    placeholder="BACE1"
)
target_steps = [
    "Search for or design compounds that bind to or affect the target.",
    "Assess compound-target interactions (docking, structure analysis).",
    "Optimize and validate promising compounds."
]
st.markdown("**Procedure Steps:**")
for i, step in enumerate(target_steps, 1):
    st.markdown(f"**Step {i}:** {step}")

# Compound Section
st.header("3. Compound-Driven Discovery")
compound_input = st.text_input(
    "Enter a compound name (e.g., aspirin, ibuprofen, SMILES string)",
    value=st.session_state.get("compound_input", ""),
    placeholder="aspirin"
)
compound_steps = [
    "Analyze the compound’s properties and known targets.",
    "Predict new uses or effects (repurposing).",
    "Validate efficacy and safety for new indications."
]
st.markdown("**Procedure Steps:**")
for i, step in enumerate(compound_steps, 1):
    st.markdown(f"**Step {i}:** {step}")

# Input validation helpers
def is_valid_disease(text):
    # Basic: at least 3 chars, contains a space or common disease word
    return bool(text) and (len(text) > 3) and (" " in text or any(w in text.lower() for w in ["disease", "cancer", "syndrome", "disorder"]))

def is_valid_target(text):
    # Basic: all caps, 2-10 chars, no spaces, not a PMID/DOI/number
    if not (bool(text) and text.isalnum() and text.isupper() and 2 <= len(text) <= 10):
        return False
    # Disallow common non-target patterns
    if text.startswith("PMID") or text.startswith("DOI") or text.isdigit():
        return False
    return True

def is_valid_compound(text):
    # Basic: at least 3 chars, not all caps, no numbers only
    return bool(text) and len(text) > 2 and not text.isupper() and not text.isdigit()


# Use session_state to persist outputs
if 'disease_output' not in st.session_state:
    st.session_state['disease_output'] = None
if 'target_output' not in st.session_state:
    st.session_state['target_output'] = None
if 'compound_output' not in st.session_state:
    st.session_state['compound_output'] = None


# Disease section submit
if st.button("Submit Disease Query"):
    if not is_valid_disease(disease_input):
        st.warning("Please enter a valid disease name (e.g., Alzheimer's disease, pancreatic cancer).")
    else:
        # If disease is in mapping, show mapped protein targets and allow user to select one for AlphaFold structure
        mapped_targets = disease_to_protein.get(disease_input)
        if mapped_targets:
            st.session_state['disease_output'] = (None, disease_input)
            st.session_state['mapped_targets'] = mapped_targets
        else:
            try:
                response = requests.get(f"http://127.0.0.1:8000/full_workflow?query={disease_input}", timeout=15)
                if response.status_code == 200:
                    result = response.json()
                    st.session_state['disease_output'] = (result, disease_input)
                else:
                    st.session_state['disease_output'] = (f"API error: {response.status_code}", None)
            except requests.RequestException as e:
                st.session_state['disease_output'] = (f"Request failed: {e}", None)


# Display disease output or mapped targets
if st.session_state['disease_output']:
    result, input_val = st.session_state['disease_output']
    st.markdown("**Disease Query Output:**")
    # If mapped_targets is set in session_state, show mapped protein targets for AlphaFold
    mapped_targets = st.session_state.get('mapped_targets')
    if mapped_targets:
        st.success("Mapped protein targets for this disease (for AlphaFold structure queries):")
        # Show both symbol and UniProt in dropdown, but use UniProt for AlphaFold
        display_options = [f"{symbol} ({uniprot})" for symbol, uniprot in mapped_targets]
        selected_idx = st.selectbox(
            "Select a protein target to view AlphaFold structure:",
            range(len(display_options)),
            format_func=lambda i: display_options[i],
            key="alphafold_target_select"
        )
        selected_symbol, selected_uniprot = mapped_targets[selected_idx]
        if st.button("Get AlphaFold Structure for Selected Target"):
            alphafold_url = f"https://alphafold.ebi.ac.uk/entry/{selected_uniprot}"
            st.markdown(f"[View AlphaFold Structure for {selected_symbol} ({selected_uniprot})]({alphafold_url})")
            st.info(f"AlphaFold structure for {selected_symbol} ({selected_uniprot}) can be viewed or downloaded from the above link.")
        if st.button("Use selected protein as input for Target-Driven Discovery"):
            st.session_state["target_input"] = selected_symbol
            st.session_state["target_uniprot"] = selected_uniprot
            st.success(f"Target input set to: {selected_symbol} (UniProt: {selected_uniprot})")
    elif isinstance(result, dict):
        # Try both /full_workflow and /discovery output structures
        if "discovery" in result and isinstance(result["discovery"], dict):
            structure_msg = result["discovery"].get("structure", "")
            suggested_targets = result["discovery"].get("suggested_targets")
        else:
            structure_msg = result.get("structure", "")
            suggested_targets = result.get("suggested_targets")
        if structure_msg:
            if is_pdb_content(structure_msg):
                st.success("AlphaFold structure found and downloaded automatically.")
                st.download_button(
                    label="Download AlphaFold PDB",
                    data=structure_msg,
                    file_name=f"{input_val}.pdb",
                    mime="chemical/x-pdb"
                )
            else:
                download_url = extract_alphafold_url(structure_msg)
                if download_url:
                    st.warning("AlphaFold structure not found online for this query.")
                    st.markdown(f"[Click here to download from AlphaFold]({download_url})")
                else:
                    st.info(structure_msg)
        # Display suggested targets if available
        if suggested_targets and isinstance(suggested_targets, list) and len(suggested_targets) > 0:
            st.success("Suggested targets for this disease (from BioBERT/NER):")
            selected_target = st.selectbox(
                "Select a target to use as input for the next step:",
                suggested_targets,
                key="target_select_disease"
            )
            if st.button("Use selected target as input for Target-Driven Discovery"):
                st.session_state["target_input"] = selected_target
                st.success(f"Target input set to: {selected_target}")
            # New: Button to find compounds for all targets
            if st.button("Find compounds for all targets"):
                from tools.pubchem_target import get_compounds_for_target
                from tools.chembl_target import get_chembl_compounds_for_target
                all_target_compounds = {}
                for t in suggested_targets:
                    pubchem = get_compounds_for_target(t)
                    chembl = get_chembl_compounds_for_target(t)
                    all_target_compounds[t] = {"pubchem": pubchem, "chembl": chembl}
                st.session_state["all_target_compounds"] = all_target_compounds
            # Display results if available
            if "all_target_compounds" in st.session_state:
                st.markdown("### Compounds for All Suggested Targets:")
                for t, sources in st.session_state["all_target_compounds"].items():
                    with st.expander(f"{t}"):
                        st.write("**PubChem Compounds:**")
                        if sources["pubchem"] and isinstance(sources["pubchem"], list) and len(sources["pubchem"]) > 0:
                            for c in sources["pubchem"]:
                                st.write(c)
                        else:
                            st.info("No PubChem compounds found.")
                        st.write("**ChEMBL Compounds:**")
                        if sources["chembl"] and isinstance(sources["chembl"], list) and len(sources["chembl"]) > 0:
                            for c in sources["chembl"]:
                                st.write(c)
                        else:
                            st.info("No ChEMBL compounds found.")
        st.json(result)
    else:
        st.error(result)


# Target section submit
if st.button("Submit Target Query"):
    if not is_valid_target(target_input):
        st.warning("Please enter a valid gene/protein target (e.g., BACE1, APP, MAPT). Do not use PMIDs, DOIs, or numbers.")
    else:
        try:
            response = requests.get(f"http://127.0.0.1:8000/full_workflow?query={target_input}", timeout=15)
            if response.status_code == 200:
                result = response.json()
                st.session_state['target_output'] = (result, target_input)
            else:
                st.session_state['target_output'] = (f"API error: {response.status_code}", None)
        except requests.RequestException as e:
            st.session_state['target_output'] = (f"Request failed: {e}", None)

# Display target output
if st.session_state['target_output']:
    result, input_val = st.session_state['target_output']
    st.markdown("**Target Query Output:**")
    compounds_for_target = None
    # Try to extract compounds_for_target from various possible locations
    if isinstance(result, dict):
        # If result is from /full_workflow, check result['discovery']
        if "discovery" in result and isinstance(result["discovery"], dict):
            compounds_for_target = result["discovery"].get("compounds_for_target")
            structure_msg = result["discovery"].get("structure", "")
        else:
            compounds_for_target = result.get("compounds_for_target")
            structure_msg = result.get("structure", "")
        # Show structure info as before
        if structure_msg:
            if is_pdb_content(structure_msg):
                st.success("AlphaFold structure found and downloaded automatically.")
                st.download_button(
                    label="Download AlphaFold PDB",
                    data=structure_msg,
                    file_name=f"{input_val}.pdb",
                    mime="chemical/x-pdb"
                )
            else:
                download_url = extract_alphafold_url(structure_msg)
                if download_url:
                    st.warning("AlphaFold structure not found online for this query.")
                    st.markdown(f"[Click here to download from AlphaFold]({download_url})")
                else:
                    st.info(structure_msg)
        # Display suggested compounds if available (PubChem)
        if compounds_for_target and isinstance(compounds_for_target, list) and len(compounds_for_target) > 0:
            # Check for PubChem API error in the first element
            if isinstance(compounds_for_target[0], dict) and "error" in compounds_for_target[0]:
                st.warning(f"PubChem API error: {compounds_for_target[0]['error']}. No compounds found for this target. Try another target or check the spelling.")
            else:
                st.success("Suggested compounds for this target (from PubChem):")
                pubchem_options = [c if isinstance(c, str) else c.get("cid", str(c)) for c in compounds_for_target]
                selected_compound = st.selectbox(
                    "Select a PubChem compound to use as input for the next step:",
                    pubchem_options,
                    key="compound_select_target"
                )
                if st.button("Use selected PubChem compound as input for Compound-Driven Discovery"):
                    st.session_state["compound_input"] = selected_compound
                    st.success(f"Compound input set to: {selected_compound}")
        elif isinstance(compounds_for_target, list) and len(compounds_for_target) == 0:
            st.info("No compounds found for this target in PubChem. Try another target or check the spelling.")

        # Display ChEMBL compounds if available
        chembl_compounds_for_target = None
        if isinstance(result, dict):
            if "discovery" in result and isinstance(result["discovery"], dict):
                chembl_compounds_for_target = result["discovery"].get("chembl_compounds_for_target")
            else:
                chembl_compounds_for_target = result.get("chembl_compounds_for_target")
        if chembl_compounds_for_target and isinstance(chembl_compounds_for_target, list) and len(chembl_compounds_for_target) > 0:
            if isinstance(chembl_compounds_for_target[0], dict) and "error" in chembl_compounds_for_target[0]:
                st.warning(f"ChEMBL API error: {chembl_compounds_for_target[0]['error']}. No compounds found for this target in ChEMBL.")
            else:
                st.success("Suggested compounds for this target (from ChEMBL):")
                chembl_options = [
                    f"{c['chembl_id']} ({c['pref_name']})" if c.get('pref_name') else c['chembl_id']
                    for c in chembl_compounds_for_target if isinstance(c, dict) and 'chembl_id' in c
                ]
                selected_chembl = st.selectbox(
                    "Select a ChEMBL compound to use as input for the next step:",
                    chembl_options,
                    key="chembl_compound_select_target"
                )
                if st.button("Use selected ChEMBL compound as input for Compound-Driven Discovery"):
                    # Extract ChEMBL ID from selection
                    chembl_id = selected_chembl.split()[0] if " " in selected_chembl else selected_chembl
                    # Fetch canonical SMILES from ChEMBL API
                    smiles = None
                    try:
                        mol_url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id}.json"
                        mol_resp = requests.get(mol_url, timeout=10)
                        if mol_resp.status_code == 200:
                            mol_data = mol_resp.json()
                            smiles = mol_data.get("molecule_structures", {}).get("canonical_smiles")
                    except requests.RequestException:
                        smiles = None
                    if smiles:
                        st.session_state["compound_input"] = smiles
                        st.success(f"Compound input set to canonical SMILES: {smiles}")
                    else:
                        st.session_state["compound_input"] = chembl_id
                        st.warning(f"Could not fetch SMILES for {chembl_id}. Using ChEMBL ID as input.")
        st.json(result)
    else:
        st.error(result)


# Compound section submit
if st.button("Submit Compound Query"):
    if not is_valid_compound(compound_input):
        st.warning("Please enter a valid compound name (e.g., aspirin, ibuprofen).")
    else:
        try:
            response = requests.get(f"http://127.0.0.1:8000/full_workflow?query={compound_input}", timeout=15)
            if response.status_code == 200:
                result = response.json()
                st.session_state['compound_output'] = (result, compound_input)
            else:
                st.session_state['compound_output'] = (f"API error: {response.status_code}", None)
        except requests.RequestException as e:
            st.session_state['compound_output'] = (f"Request failed: {e}", None)

# Display compound output
if st.session_state['compound_output']:
    result, input_val = st.session_state['compound_output']
    st.markdown("**Compound Query Output:**")
    if isinstance(result, dict):
        structure_msg = None
        if isinstance(result, dict) and "discovery" in result and isinstance(result["discovery"], dict):
            structure_msg = result["discovery"].get("structure", "")
        elif isinstance(result, dict) and "structure" in result:
            structure_msg = result.get("structure", "")
        if structure_msg:
            if is_pdb_content(structure_msg):
                st.success("AlphaFold structure found and downloaded automatically.")
                st.download_button(
                    label="Download AlphaFold PDB",
                    data=structure_msg,
                    file_name=f"{input_val}.pdb",
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
        st.error(result)
