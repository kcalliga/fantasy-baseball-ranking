import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Research Lab", page_icon="🧪", layout="wide")

st.title("🧪 Advanced Research Lab")
st.write("Upload high-dimensional datasets to find hidden statistical relationships.")

# --- 1. DATA UPLOAD ---
st.sidebar.header("📁 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload CSV for Analysis", type=["csv"])

if not uploaded_file:
    st.info("💡 Please upload a CSV file in the sidebar to begin analysis. (e.g., a full Statcast export with 50+ columns)")
    st.stop()

# Load data
df = pd.read_csv(uploaded_file)
df.columns = df.columns.str.lower()

# Clean numeric data
numeric_df = df.select_dtypes(include=[np.number]).drop(columns=['playerid', 'week_num', 'year'], errors='ignore')

if numeric_df.empty:
    st.error("No numeric columns found in the uploaded file.")
    st.stop()

# --- 2. TARGET ANALYSIS (The "Non-Clunky" View) ---
st.header("🎯 Target Variable Focus")
st.write("Pick one outcome (e.g., 'HR') to see which 'raw' metrics correlate most strongly with it.")

target_col = st.selectbox("Select Target Variable:", options=numeric_df.columns, index=0)

# Calculate correlations for just that target
target_corr = numeric_df.corr()[target_col].sort_values(ascending=False)
# Remove the target's correlation with itself
target_corr = target_corr.drop(labels=[target_col])

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Strongest Relationships")
    st.write(f"Top 10 metrics driving **{target_col.upper()}**:")
    st.dataframe(target_corr.head(10), use_container_width=True)

with col2:
    # Bar chart of correlations
    fig_target = px.bar(
        x=target_corr.head(15).index, 
        y=target_corr.head(15).values,
        labels={'x': 'Metric', 'y': 'Correlation Coefficient'},
        title=f"Correlation with {target_col.upper()}",
        color=target_corr.head(15).values,
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig_target, use_container_width=True)

st.divider()

# --- 3. THE INTERACTIVE MASTER MATRIX ---
st.header("🌐 Interactive Master Matrix")
st.write("Use the box-zoom tool (top right of chart) to dive into specific clusters of data.")

# Sidebar filter for the big matrix so it's not overwhelmed
all_cols = numeric_df.columns.tolist()
selected_for_matrix = st.multiselect(
    "Filter Matrix Columns (Defaults to first 25):", 
    options=all_cols, 
    default=all_cols[:25] if len(all_cols) > 25 else all_cols
)

if len(selected_for_matrix) > 1:
    corr_matrix = numeric_df[selected_for_matrix].corr()
    
    # Use Plotly Heatmap for zooming and hovering
    fig_heat = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        hoverongaps=False,
        hovertemplate='X: %{x}<br>Y: %{y}<br>Corr: %{z:.3f}<extra></extra>'
    ))
    
    fig_heat.update_layout(
        height=700,
        title="Master Correlation Map (Zoomable)",
        xaxis_nticks=36
    )
    
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.warning("Select at least 2 columns for the matrix.")

# --- 4. OUTLIER DISCOVERY ---
st.divider()
st.header("🔭 Outlier Discovery (X vs Y)")
col_x, col_y = st.columns(2)
x_var = col_x.selectbox("Predictor (X):", options=all_cols, index=0)
y_var = col_y.selectbox("Outcome (Y):", options=all_cols, index=1)

fig_scatter = px.scatter(
    df, x=x_var, y=y_var, 
    hover_name='name' if 'name' in df.columns else None,
    trendline="ols",
    title=f"{x_var.upper()} vs {y_var.upper()}",
    template="plotly_dark"
)
st.plotly_chart(fig_scatter, use_container_width=True)