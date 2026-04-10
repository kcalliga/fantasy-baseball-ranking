import streamlit as st

# Configure the main page layout
st.set_page_config(
    page_title="Fantasy Baseball Tracker",
    page_icon="⚾",
    layout="wide"
)

st.title("⚾ Fantasy Baseball Rating System")

st.markdown("""
Welcome to your custom Fantasy Baseball tracking platform. 

This tool is designed to ingest FanGraphs CSV data and evaluate it against your specific league scoring settings. Use the sidebar to navigate between different tools:

* **League Rules:** View and manage scoring configurations for Fantrax, Yahoo, and RTSports.
* **System Evaluator:** Upload historical FanGraphs projections (ZiPS, Steamer, etc.) to test model accuracy.
* **Roster Trends:** Track your current team's performance against expected points.
""")

st.info("👈 Select a tool from the sidebar to get started.")

# You can add high-level summary stats or quick links here later
st.divider()
st.write("Ready for CSV ingestion.")
