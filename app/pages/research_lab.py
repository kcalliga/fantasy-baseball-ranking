import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import glob
import os

st.set_page_config(page_title="Research Lab", page_icon="🧪", layout="wide")

st.title("🧪 Advanced Research Lab")
st.write("Perform ad-hoc analysis, correlations, and deeper statistical dives.")

# --- 1. DATA SELECTION ---
BASE_STATS_PATH = "data/weekly_stats"
existing_years = [d for d in os.listdir(BASE_STATS_PATH) if os.path.isdir(os.path.join(BASE_STATS_PATH, d))]
selected_year = st.sidebar.selectbox("Season Year", sorted(existing_years, reverse=True))
player_type = st.sidebar.radio("Analyze:", ["Batters", "Pitchers"])
YEAR_FOLDER = os.path.join(BASE_STATS_PATH, selected_year, player_type.lower())

# Load the latest weekly file for analysis
weekly_files = sorted(glob.glob(os.path.join(YEAR_FOLDER, "*.csv")))

if not weekly_files:
    st.info("No data found to analyze.")
    st.stop()

# Use the most recent week's data for the cross-sectional correlation
df = pd.read_csv(weekly_files[-1])
df.columns = df.columns.str.lower()

# --- 2. CORRELATION MATRIX TOOL ---
st.header("📊 Variable Correlation Matrix")
st.write("""
Select the statistics you want to compare. This helps identify which 'raw' metrics 
(like Exit Velocity or Bat Speed) have the strongest relationship with fantasy outcomes.
""")

# Only allow numeric columns for correlation
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
# Filter out boring columns like 'playerid' or 'week_num'
ignore_cols = ['playerid', 'week_num', 'year']
filtered_cols = [c for c in numeric_cols if c not in ignore_cols]

selected_metrics = st.multiselect(
    "Select Metrics to Correlate:", 
    options=filtered_cols, 
    default=filtered_cols[:8] if len(filtered_cols) > 8 else filtered_cols
)

if len(selected_metrics) < 2:
    st.warning("Please select at least two metrics to see a correlation.")
else:
    # Calculate Correlation
    corr_matrix = df[selected_metrics].corr()

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax, center=0)
    plt.title(f"Correlation Matrix: {player_type}")
    st.pyplot(fig)

    # Key Insights Section
    st.subheader("💡 Key Findings")
    # Identify the highest correlation in the matrix (excluding 1.0)
    stack = corr_matrix.unstack()
    strongest = stack[stack < 1].sort_values(ascending=False).head(2)
    
    if not strongest.empty:
        var1, var2 = strongest.index[0]
        val = strongest.values[0]
        st.write(f"The strongest relationship in your selection is between **{var1.upper()}** and **{var2.upper()}** ({val:.2f}).")

# --- 3. SCATTER PLOT DIV (The 'Why' Factor) ---
st.divider()
st.header("🎯 Deep Dive: X vs Y")

col1, col2 = st.columns(2)
x_axis = col1.selectbox("X-Axis (Predictor):", options=filtered_cols, index=0)
y_axis = col2.selectbox("Y-Axis (Outcome):", options=filtered_cols, index=1)

fig_scatter = sns.lmplot(data=df, x=x_axis, y=y_axis, aspect=1.5, scatter_kws={'alpha':0.5})
plt.title(f"Relationship: {x_axis.upper()} vs {y_axis.upper()}")
st.pyplot(plt.gcf())