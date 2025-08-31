import streamlit as st
import requests

st.title("Drug Discovery AI Assistant")
query = st.text_input("Enter disease, target, or compound:")

if st.button("Submit"):
    if query:
        try:
            response = requests.get(f"http://127.0.0.1:8000/full_workflow?query={query}")
            if response.status_code == 200:
                st.json(response.json())
            else:
                st.error(f"API error: {response.status_code}")
        except Exception as e:
            st.error(f"Request failed: {e}")
    else:
        st.warning("Please enter a query.")
