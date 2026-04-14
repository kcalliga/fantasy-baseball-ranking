import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="System Evaluator", page_icon="⚖️", layout="wide")

st.title("⚖️ Projection System Evaluator")
st.markdown("Upload multiple projection systems to compare their accuracy head-to-head against actual stats.")

# --- 1. FILE UPLOADS ---
st.subheader("Upload FanGraphs CSVs")
col1, col2 = st.columns(2)

with col1:
    # Set accept_multiple_files to True
    proj_files = st.file_uploader("Upload Projections (e.g., ZiPS, Steamer)", type=["csv"], accept_multiple_files=True)
with col2:
    actual_file = st.file_uploader("Upload Actual Stats", type=["csv"])

st.divider()

# --- 2. DATA PROCESSING ---
if proj_files and actual_file:
    # Load and clean the actuals file once
    df_actual = pd.read_csv(actual_file)
    df_actual.columns = df_actual.columns.str.lower()
    
    if 'playerid' not in df_actual.columns:
        st.error("Could not find 'playerid' in the Actuals CSV. Please check your FanGraphs export.")
        st.stop()
        
    df_actual['playerid'] = df_actual['playerid'].astype(str)
    
    # Dictionaries and lists to store results for multiple systems
    system_metrics = []
    processed_dfs = {}
    
    # Find common numeric columns based on the FIRST uploaded projection file to build the UI
    df_first_proj = pd.read_csv(proj_files[0])
    df_first_proj.columns = df_first_proj.columns.str.lower()
    common_cols = [c for c in df_first_proj.columns if c in df_actual.columns and pd.api.types.is_numeric_dtype(df_first_proj[c])]
    numeric_stats = [c for c in common_cols if c != 'playerid']

    # --- 3. UI CONTROLS ---
    st.sidebar.header("Evaluation Settings")
    
    available_stats = sorted([s.upper() for s in numeric_stats])
    default_stats = [s for s in ['HR', 'SB', 'R', 'RBI', 'SO'] if s in available_stats]
    
    selected_stats = st.sidebar.multiselect(
        "Select Stats to Evaluate", 
        available_stats,
        default=default_stats
    )
    
    if not selected_stats:
        st.warning("Please select at least one stat from the sidebar to evaluate.")
        st.stop()

    # --- PROCESS EACH UPLOADED SYSTEM ---
    for p_file in proj_files:
        # Extract a clean system name from the file name (e.g., "zips_2025.csv" -> "zips_2025")
        system_name = p_file.name.replace('.csv', '').upper()
        
        # REWIND THE FILE POINTER TO THE BEGINNING!
        p_file.seek(0)
        
        # Load and clean this specific projection file
        df_proj = pd.read_csv(p_file)
        df_proj.columns = df_proj.columns.str.lower()
        
        if 'playerid' not in df_proj.columns:
            st.warning(f"Skipping {system_name}: No 'playerid' column found.")
            continue
            
        df_proj['playerid'] = df_proj['playerid'].astype(str)
        
        # Merge this system with the actuals
        df = pd.merge(df_proj, df_actual, on=['playerid', 'name'], suffixes=('_proj', '_act'))
        
        # Initialize tracking columns
        df['Total_Scaled_Error'] = 0.0
        df['Total_Absolute_Error'] = 0.0
        df['Total_Actual_Volume'] = 0.0
        display_columns = ['name']
        
        for stat in selected_stats:
            stat_lower = stat.lower()
            proj_col = f'{stat_lower}_proj'
            act_col = f'{stat_lower}_act'
            diff_col = f'{stat}_Diff'
            abs_col = f'{stat}_Abs_Err'
            
            # If the stat is missing in this specific file, skip it gracefully
            if proj_col not in df.columns or act_col not in df.columns:
                continue
            
            df[diff_col] = df[act_col] - df[proj_col]
            df[abs_col] = df[diff_col].abs()
            
            df['Total_Absolute_Error'] += df[abs_col]
            df['Total_Actual_Volume'] += df[act_col].abs()
            
            # Scaled error
            stat_std = df[act_col].std() + 1e-9
            df[f'{stat}_Scaled'] = df[abs_col] / stat_std
            df['Total_Scaled_Error'] += df[f'{stat}_Scaled']
            
            display_columns.extend([proj_col, act_col, diff_col])
            
        display_columns.append('Total_Scaled_Error')
        
        # Calculate system-wide metrics
        system_scaled_error = df['Total_Scaled_Error'].mean()
        
        total_abs_error = df['Total_Absolute_Error'].sum()
        total_actuals = df['Total_Actual_Volume'].sum()
        system_wape = (total_abs_error / total_actuals) * 100 if total_actuals > 0 else 0.0
        
        # Store metrics for the leaderboard
        system_metrics.append({
            "System Name": system_name,
            "Players Evaluated": len(df),
            "System WAPE (%)": round(system_wape, 2),
            "Scaled Error Index": round(system_scaled_error, 3)
        })
        
        # Save the processed dataframe for the drill-down view
        processed_dfs[system_name] = df[display_columns].copy()

# --- 4. THE HEAD-TO-HEAD LEADERBOARD ---
    if system_metrics:
        st.subheader("🏆 Head-to-Head System Leaderboard")
        st.caption(f"Based on accuracy for: {', '.join(selected_stats)}")
        
        # Convert metrics to a dataframe and sort by best Scaled Error Index (lowest is best)
        df_leaderboard = pd.DataFrame(system_metrics).sort_values(by="Scaled Error Index", ascending=True)
        st.dataframe(df_leaderboard, use_container_width=True, hide_index=True)
        
        # --- AUTOMATED TAKEAWAY ---
        if len(df_leaderboard) > 1:
            # Extract the winning system's stats
            best_system = df_leaderboard.iloc[0]['System Name']
            best_scaled = df_leaderboard.iloc[0]['Scaled Error Index']
            best_wape = df_leaderboard.iloc[0]['System WAPE (%)']
            
            # Extract the second-place system to show the margin of victory
            runner_up = df_leaderboard.iloc[1]['System Name']
            
            st.success(f"**💡 The Verdict:** Based on your selected categories, **{best_system}** was the most accurate projection system. "
                       f"It edged out {runner_up} with the lowest Scaled Error Index ({best_scaled}), meaning it did the best job "
                       f"avoiding massive, irreplaceable misses. Overall, its raw volume projections were off by an average of {best_wape}%.")
        elif len(df_leaderboard) == 1:
            st.info(f"**💡 System Performance:** You are currently evaluating **{df_leaderboard.iloc[0]['System Name']}** in isolation. "
                    f"Upload another system (like Steamer or ATC) into the Projections box to see a head-to-head comparison!")
            
        st.divider()
        
        # --- 5. PLAYER LEADERBOARD (DRILL DOWN) ---
        st.write("### 🔍 Player-Level Drill Down")
        
        # Let the user pick which system's player errors they want to look at
        view_system = st.selectbox("Select System to View Player Errors:", list(processed_dfs.keys()))
        
        if view_system:
            display_df = processed_dfs[view_system]
            display_df = display_df.sort_values(by='Total_Scaled_Error', ascending=False)
            display_df.rename(columns={'name': 'Player Name', 'Total_Scaled_Error': 'Total Scaled Error'}, inplace=True)
            display_df['Total Scaled Error'] = display_df['Total Scaled Error'].round(3)
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.info("Awaiting file uploads. Drop your Projections and Actuals CSVs above.")