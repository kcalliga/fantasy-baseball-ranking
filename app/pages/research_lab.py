import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Research Lab", page_icon="🧪", layout="wide")

# --- 1. DEFINITIONS DICTIONARY ---
# You can expand this as you add more exotic Statcast data
STAT_DEFINITIONS = {
    'hr': "Home Runs: Balls hit over the fence for four bases.",
    'bat_speed': "Average speed of the sweet spot of the bat at contact.",
    'barrel_pct': "Percentage of batted balls with an optimal combination of exit velocity and launch angle.",
    'hard_hit_pct': "Percentage of balls hit with an exit velocity of 95 mph or higher.",
    'ev': "Exit Velocity: The speed of the ball as it comes off the bat.",
    'la': "Launch Angle: The vertical angle at which the ball leaves the bat.",
    'max_ev': "The highest exit velocity recorded by a player in the selected period.",
    'dist': "Estimated distance the ball traveled.",
    'xwoba': "Expected Weighted On-Base Average: Measures the quality of contact rather than actual results.",
    'velocity': "In this app: The change in a player's Heat Index from the previous week.",
    'heat index': "In this app: A Z-score measuring weekly performance relative to projected pace.",
    'pa': "Plate Appearances: Total number of completed turns at bat.",
    'ip': "Innings Pitched: The number of innings a pitcher has completed."
}

def get_desc(stat_name):
    return STAT_DEFINITIONS.get(stat_name.lower(), "Standard statistical metric.")

st.title("🧪 Advanced Research Lab")

# --- 2. DATA UPLOAD ---
st.sidebar.header("📁 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload CSV for Analysis", type=["csv"])

if not uploaded_file:
    st.info("💡 Please upload a CSV file (e.g., Statcast export) to begin.")
    st.stop()

df = pd.read_csv(uploaded_file)
df.columns = df.columns.str.lower()
numeric_df = df.select_dtypes(include=[np.number]).drop(columns=['playerid', 'week_num', 'year'], errors='ignore')

# --- 3. TARGET ANALYSIS ---
st.header("🎯 Target Variable Focus")
target_col = st.selectbox("Select Target Variable:", options=numeric_df.columns, index=0)

target_corr = numeric_df.corr()[target_col].sort_values(ascending=False).drop(labels=[target_col])

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Strongest Drivers")
    # Display table with tooltips
    formatted_corr = pd.DataFrame(target_corr.head(10)).reset_index()
    formatted_corr.columns = ['Metric', 'Correlation']
    st.dataframe(formatted_corr, use_container_width=True, hide_index=True)
    st.caption(f"**Definition:** {get_desc(target_col)}")

with col2:
    # Adding description to hover data
    fig_target = px.bar(
        x=target_corr.head(15).index, 
        y=target_corr.head(15).values,
        labels={'x': 'Metric', 'y': 'Correlation'},
        title=f"What drives {target_col.upper()}?",
        color=target_corr.head(15).values,
        color_continuous_scale='RdYlGn'
    )
    # Map descriptions into the hover template
    descriptions = [get_desc(m) for m in target_corr.head(15).index]
    fig_target.update_traces(customdata=descriptions, hovertemplate="<b>%{x}</b><br>Corr: %{y:.3f}<br>%{customdata}")
    st.plotly_chart(fig_target, use_container_width=True)

st.divider()

# --- 4. THE INTERACTIVE MASTER MATRIX ---
st.header("🌐 Interactive Master Matrix")
all_cols = numeric_df.columns.tolist()
selected_for_matrix = st.multiselect("Select Columns:", options=all_cols, default=all_cols[:20])

if len(selected_for_matrix) > 1:
    corr_matrix = numeric_df[selected_for_matrix].corr()
    
    # Custom hover data for the heatmap
    # We create a 2D array of descriptions matching the matrix size
    hover_text = []
    for y in corr_matrix.index:
        row_text = []
        for x in corr_matrix.columns:
            row_text.append(f"X: {get_desc(x)}<br>Y: {get_desc(y)}")
        hover_text.append(row_text)

    fig_heat = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        customdata=hover_text,
        hovertemplate='<b>%{x} vs %{y}</b><br>Correlation: %{z:.3f}<br><br>%{customdata}<extra></extra>'
    ))
    fig_heat.update_layout(height=700, title="Zoomable Correlation Map")
    st.plotly_chart(fig_heat, use_container_width=True)

# --- 5. OUTLIER DISCOVERY ---
st.divider()
st.header("🔭 Outlier Discovery (X vs Y)")
col_x, col_y = st.columns(2)
x_var = col_x.selectbox("Predictor (X):", options=all_cols, index=0)
y_var = col_y.selectbox("Outcome (Y):", options=all_cols, index=1)

fig_scatter = px.scatter(
    df, x=x_var, y=y_var, 
    hover_name='name' if 'name' in df.columns else None,
    trendline="ols",
    template="plotly_dark"
)

# Add definitions to scatter hover
scatter_hover = f"<b>X:</b> {get_desc(x_var)}<br><b>Y:</b> {get_desc(y_var)}"
fig_scatter.update_traces(hovertemplate=f"%{{hovertext}}<br>{x_var}: %{{x}}<br>{y_var}: %{{y}}<br><br>{scatter_hover}")

st.plotly_chart(fig_scatter, use_container_width=True)