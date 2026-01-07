import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.title("Smart Loadshedding Advisor")

st.text_input("Search area")

if st.button("Test API Health"):
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        st.success(response.json())
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
