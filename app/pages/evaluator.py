import streamlit as st
import pandas as pd
import yaml
import os

st.set_page_config(page_title="System Evaluator", page_icon="⚖️", layout="wide")

CONFIG_PATH = "config/leagues.yaml"

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as file:
            return yaml.safe_load(file) or {}
    return {}

st.title("⚖️ Projection System Evaluator")
st.markdown("Compare historical FanGraphs projections (e.g., ZiPS, Steamer) against actual end-of-season stats.")

config = load_config()

if not config:
    st.warning("No league rules found. Please add a league in the 'League Rules' menu first.")
    st.stop()

# --- 1. SETTINGS & UPLOADS ---
st.sidebar.header("Evaluation Settings")
selected_league = st.sidebar.selectbox("Select League Scoring", list(config.keys()))
player_pool = st.sidebar.radio("Analyze:", ["Hitters", "Pitchers"])

st.subheader(f"Upload FanGraphs CSVs ({player_pool})")
col1, col2 = st.columns(2)

with col1:
    proj_file = st.file_uploader("Upload Projections (e.g., ZiPS)", type=["csv"])
with col2:
    actual_file = st.file_uploader("Upload Actual Stats", type=["csv"])

st.divider()

# --- 2. DATA PROCESSING & VISUALIZATION ---
if proj_file and actual_file:
    # Read the CSVs into Pandas DataFrames
    df_proj = pd.read_csv(proj_file)
    df_actual = pd.read_csv(actual_file)
    
    st.success("Files loaded successfully! Merging datasets...")

    # NOTE: In FanGraphs data, it is best to merge on 'playerid' to avoid name mismatches.
    # For this skeleton, we will ensure 'Name' and 'playerid' exist before merging.
    if 'playerid' in df_proj.columns and 'playerid' in df_actual.columns:
        # We add suffixes to tell the columns apart after merging (e.g., HR_proj vs HR_actual)
        df_merged = pd.merge(df_proj, df_actual, on=['playerid', 'Name'], suffixes=('_proj', '_actual'))
        
        # --- MOCK CALCULATION FOR UI TESTING ---
        # In the future, this math will be moved to your src/evaluator.py file.
        # For the skeleton, we will just generate mock total points to show the layout.
        import numpy as np
        df_merged['Projected_Points'] = np.random.randint(200, 600, df_merged.shape[0])
        df_merged['Actual_Points'] = np.random.randint(150, 650, df_merged.shape[0])
        df_merged['Differential'] = df_merged['Actual_Points'] - df_merged['Projected_Points']
        
        # Filter down to the columns we want to display
        display_df = df_merged[['Name', 'Projected_Points', 'Actual_Points', 'Differential']]
        
        # --- 3. DASHBOARD METRICS & CHARTS ---
        st.subheader(f"Evaluation Results for {selected_league}")
        
        # High-level metrics
        met1, met2, met3 = st.columns(3)
        met1.metric("Players Evaluated", len(display_df))
        met2.metric("Mean Absolute Error (Mock)", "34.2 pts")
        met3.metric("System Tendency (Mock)", "Over-projected by 5%")
        
        st.write("### Top Discrepancies")
        st.write("Players where the projection system was the least accurate:")
        
        # Sort by the biggest miss (absolute differential)
        display_df['Abs_Diff'] = display_df['Differential'].abs()
        display_df = display_df.sort_values(by='Abs_Diff', ascending=False).drop(columns=['Abs_Diff'])
        
        st.dataframe(display_df.head(15), use_container_width=True)
        
    else:
        st.error("Could not find 'playerid' in one or both CSVs. Please ensure you are using raw FanGraphs exports.")
        
else:
    st.info("Awaiting file uploads. Please drop your CSVs in the boxes above.")