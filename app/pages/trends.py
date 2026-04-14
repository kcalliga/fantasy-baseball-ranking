import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Roster Trends", page_icon="📈", layout="wide")

st.title("📈 Roster Trends & Tracking")

# 1. Sidebar settings
st.sidebar.header("Calculation Settings")
selected_league = st.sidebar.selectbox("Select League", ["Fantrax", "Yahoo", "RTSports"])
current_week = st.sidebar.slider("Current Week of Season", 1, 24, 4)

# 2. CSV Uploaders side-by-side
col1, col2 = st.columns(2)
with col1:
    roster_file = st.file_uploader("Upload Current Roster (CSV)", type=["csv"])
with col2:
    stats_file = st.file_uploader("Upload Weekly Stats (CSV)", type=["csv"])

st.divider()

# 3. Main Display Area
st.subheader(f"Player Trend Analysis - {selected_league} (Week {current_week})")

# If no files are uploaded, show a placeholder mock graph so you can see "the look"
if not roster_file and not stats_file:
    st.info("Upload your FanGraphs CSV files above to generate live trend lines.")
    
    st.write("#### Example Trend: Bryce Harper (Mock Data)")
    
    # Generating fake data to demonstrate the graph
    weeks = list(range(1, 25))
    expected_points = [x * 18 for x in weeks] # Smooth expected trajectory
    actual_points = [15, 38, 50, 75] + [None] * 20 # Jagged actual performance up to week 4
    
    chart_data = pd.DataFrame({
        "Expected Points": expected_points,
        "Actual Points": actual_points
    }, index=weeks)
    
    # Streamlit's native line chart (we can upgrade to interactive Plotly later)
    st.line_chart(chart_data)
