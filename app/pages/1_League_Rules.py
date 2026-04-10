import streamlit as st
import yaml
import os

st.set_page_config(page_title="League Rules", page_icon="⚙️", layout="wide")

# Path to your configuration file
CONFIG_PATH = "config/leagues.yaml"

# Helper function to load the YAML file
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as file:
            return yaml.safe_load(file) or {}
    return {}

# Helper function to save to the YAML file
def save_config(data):
    # Ensure the config directory exists
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as file:
        yaml.dump(data, file, sort_keys=False)

st.title("⚙️ League Scoring Rules")

# --- 1. DISPLAY EXISTING LEAGUES ---
st.header("Current Leagues")
config = load_config()

if not config:
    st.info("No leagues found in leagues.yaml. Add one below!")
else:
    # Display each league in an expandable dropdown
    for league_name, rules in config.items():
        with st.expander(f"📖 {league_name}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Hitter Categories**")
                # Using a dataframe makes the dictionary look like a clean table
                if "hitters" in rules:
                    st.dataframe(rules["hitters"], use_container_width=True)
            with col2:
                st.write("**Pitcher Categories**")
                if "pitchers" in rules:
                    st.dataframe(rules["pitchers"], use_container_width=True)

st.divider()

# --- 2. ADD A NEW LEAGUE FORM ---
st.header("➕ Add New League")

# We compile a list of all the standard categories utilized across your leagues
hitter_cats = ["1B", "2B", "3B", "HR", "RBI", "R", "BB", "SB", "K", "CS", "HBP"]
pitcher_cats = ["W", "L", "SV", "QS", "K", "BB", "IP", "OUT", "H", "ER", "HBP"]

with st.form("new_league_form"):
    new_league_name = st.text_input("League Name (e.g., ESPN_Public)", placeholder="Enter league name...")
    
    st.subheader("Hitters (Point Values)")
    hitter_inputs = {}
    h_cols = st.columns(6)
    # Loop through categories and create an input box for each
    for i, cat in enumerate(hitter_cats):
        hitter_inputs[cat] = h_cols[i % 6].number_input(cat, value=0.0, step=0.5, format="%.2f", key=f"h_{cat}")

    st.subheader("Pitchers (Point Values)")
    pitcher_inputs = {}
    p_cols = st.columns(6)
    for i, cat in enumerate(pitcher_cats):
        pitcher_inputs[cat] = p_cols[i % 6].number_input(cat, value=0.0, step=0.5, format="%.2f", key=f"p_{cat}")