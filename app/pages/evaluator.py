import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="System Evaluator", page_icon="⚖️", layout="wide")

st.title("⚖️ Projection System Evaluator")
st.markdown("Evaluate raw statistical accuracy of projection systems (e.g., ZiPS, Steamer) ignoring fantasy point values.")

# --- 1. FILE UPLOADS ---
st.subheader("Upload FanGraphs CSVs")
col1, col2 = st.columns(2)

with col1:
    proj_file = st.file_uploader("Upload Projections (e.g., ZiPS)", type=["csv"])
with col2:
    actual_file = st.file_uploader("Upload Actual Stats", type=["csv"])

st.divider()

# --- 2. DATA PROCESSING ---
if proj_file and actual_file:
    df_proj = pd.read_csv(proj_file)
    df_actual = pd.read_csv(actual_file)
    
    # Standardize column names to lowercase to catch PlayerId vs playerid discrepancies
    df_proj.columns = df_proj.columns.str.lower()
    df_actual.columns = df_actual.columns.str.lower()
    
    if 'playerid' in df_proj.columns and 'playerid' in df_actual.columns:
        
        # Force both playerid columns to be strings to prevent merge errors
        df_proj['playerid'] = df_proj['playerid'].astype(str)
        df_actual['playerid'] = df_actual['playerid'].astype(str)
        
        # Merge datasets (using lowercase 'name' and 'playerid')
        df = pd.merge(df_proj, df_actual, on=['playerid', 'name'], suffixes=('_proj', '_act'))
        
        # Identify numeric columns that exist in both files to populate our dropdown
        common_cols = [c.replace('_proj', '') for c in df.columns if c.endswith('_proj')]
        numeric_stats = [c for c in common_cols if c != 'playerid' and pd.api.types.is_numeric_dtype(df[f'{c}_proj'])]
        
        # --- 3. UI CONTROLS ---
        st.sidebar.header("Evaluation Settings")
        
        # We use upper() here so the dropdown menu looks clean (e.g., "HR" instead of "hr")
        selected_stat = st.sidebar.selectbox("Select Stat to Evaluate", sorted([s.upper() for s in numeric_stats]))
        
        # Convert the selected stat back to lowercase to do the math
        selected_stat_lower = selected_stat.lower()
        proj_col = f'{selected_stat_lower}_proj'
        act_col = f'{selected_stat_lower}_act'
        
        # Player-Level Accuracy: Actual minus Projected (Positive means player beat the projection)
        df['Differential'] = df[act_col] - df[proj_col]
        df['Absolute_Error'] = df['Differential'].abs()
        
        # --- 4. SYSTEM METRICS (THE "TOTAL") ---
        st.subheader(f"Total System Accuracy for: {selected_stat}")
        
        # Calculate Mean Absolute Error (MAE) and Root Mean Square Error (RMSE) across the whole system
        mae = df['Absolute_Error'].mean()
        rmse = np.sqrt((df['Differential'] ** 2).mean())
        
        met1, met2, met3 = st.columns(3)
        met1.metric("Total Players Evaluated", len(df))
        met2.metric("Total MAE (Average Miss)", f"{mae:.2f}")
        met3.metric("Total RMSE (Weighted Miss)", f"{rmse:.2f}")
        
        st.divider()
        
        # --- 5. PLAYER LEADERBOARD (THE "EACH PLAYER") ---
        st.write(f"### Player-Level Accuracy for {selected_stat}")
        st.write("Review the individual error for every player in the dataset, sorted by the biggest misses.")
        
        # Format the display dataframe (using lowercase 'name')
        display_df = df[['name', proj_col, act_col, 'Differential', 'Absolute_Error']].copy()
        
        # Sort by the biggest absolute miss
        display_df = display_df.sort_values(by='Absolute_Error', ascending=False)
        
        # Rename columns to be cleaner in the UI
        display_df.columns = ['Player Name', 'Projected', 'Actual', 'Difference', 'Absolute Error']
        
        # Display the interactive table
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    else:
        st.error("Could not find 'playerid' in one or both CSVs. Please check your FanGraphs exports.")
else:
    st.info("Awaiting file uploads. Drop your Projections and Actuals CSVs above.")