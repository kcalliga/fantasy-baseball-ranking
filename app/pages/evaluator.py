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
        
        available_stats = sorted([s.upper() for s in numeric_stats])
        default_stats = [s for s in ['HR', 'SB', 'R', 'RBI', 'SO'] if s in available_stats]
        
        selected_stats = st.sidebar.multiselect(
            "Select Stats to Evaluate (Combined)", 
            available_stats,
            default=default_stats
        )
        
        if not selected_stats:
            st.warning("Please select at least one stat from the sidebar to evaluate.")
            st.stop()

        # Initialize a column for the Scaled Total Error
        df['Total_Scaled_Error'] = 0.0
        display_columns = ['name']
        
        # Loop through every stat the user selected
        for stat in selected_stats:
            stat_lower = stat.lower()
            proj_col = f'{stat_lower}_proj'
            act_col = f'{stat_lower}_act'
            diff_col = f'{stat}_Diff'
            abs_col = f'{stat}_Abs_Err'
            
            # Calculate the raw differential and absolute error
            df[diff_col] = df[act_col] - df[proj_col]
            df[abs_col] = df[diff_col].abs()
            
            # SCALE THE ERROR: Divide the absolute miss by the stat's standard deviation
            # We add 1e-9 to prevent a "Divide by Zero" error just in case a stat is completely blank
            stat_std = df[act_col].std() + 1e-9
            df[f'{stat}_Scaled'] = df[abs_col] / stat_std
            
            # Add this mathematically scaled error to the player's running total
            df['Total_Scaled_Error'] += df[f'{stat}_Scaled']
            
            # Add the raw columns we want to show in the final table for human readability
            display_columns.extend([proj_col, act_col, diff_col])

        # Finally, add the Total Scaled Error to the end of the display list
        display_columns.append('Total_Scaled_Error')

        # --- 4. SYSTEM METRICS (THE "TOTAL ACROSS EVERYTHING") ---
        st.subheader(f"Total System Accuracy for Selected Stats: {', '.join(selected_stats)}")
        
        # We calculate the average scaled error across the entire system
        system_scaled_error = df['Total_Scaled_Error'].mean()
        
        met1, met2 = st.columns(2)
        met1.metric("Total Players Evaluated", len(df))
        met2.metric("System Scaled Error Index", f"{system_scaled_error:.3f}")
        st.caption("*The Scaled Error Index normalizes stats by standard deviation. A lower number means the system is more accurate overall.*")
        
        st.divider()
        
        # --- 5. PLAYER LEADERBOARD ---
        st.write("### Player-Level Accuracy Dashboard")
        st.write("Review raw differences for each stat. Sorted by the highest mathematically scaled error.")
        
        # Filter the dataframe to just our display columns and sort by the biggest scaled miss
        display_df = df[display_columns].copy()
        display_df = display_df.sort_values(by='Total_Scaled_Error', ascending=False)
        
        # Rename the columns cleanly
        display_df.rename(columns={'name': 'Player Name', 'Total_Scaled_Error': 'Total Scaled Error'}, inplace=True)
        
        # Round the scaled error for a cleaner UI
        display_df['Total Scaled Error'] = display_df['Total Scaled Error'].round(3)
        
        # Display the interactive table
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    else:
        st.error("Could not find 'playerid' in one or both CSVs. Please check your FanGraphs exports.")
else:
    st.info("Awaiting file uploads. Drop your Projections and Actuals CSVs above.")