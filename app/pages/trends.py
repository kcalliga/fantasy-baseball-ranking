import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import glob
from thefuzz import process

st.set_page_config(page_title="Roster Trends", page_icon="📈", layout="wide")

st.title("📈 Roster Trends & Pace Tracker")

# --- 1. DIRECTORY CONFIGURATION ---
BASE_STATS_PATH = "data/weekly_stats"

# --- 2. SIDEBAR SETTINGS ---
st.sidebar.header("⚙️ Data Settings")
if not os.path.exists(BASE_STATS_PATH):
    os.makedirs(BASE_STATS_PATH)

existing_years = [d for d in os.listdir(BASE_STATS_PATH) if os.path.isdir(os.path.join(BASE_STATS_PATH, d))]
if "2026" not in existing_years:
    os.makedirs(os.path.join(BASE_STATS_PATH, "2026/batters"), exist_ok=True)
    os.makedirs(os.path.join(BASE_STATS_PATH, "2026/pitchers"), exist_ok=True)
    existing_years.append("2026")

selected_year = st.sidebar.selectbox("Season Year", sorted(existing_years, reverse=True))
player_type = st.sidebar.radio("Analyze:", ["Batters", "Pitchers"])
type_folder = player_type.lower()
YEAR_FOLDER = os.path.join(BASE_STATS_PATH, selected_year, type_folder)

proj_file = st.sidebar.file_uploader(f"Upload {selected_year} {player_type} Projections", type=["csv"])

# --- 3. DATA LOADING ---
weekly_files = sorted(glob.glob(os.path.join(YEAR_FOLDER, "*.csv")))
if not weekly_files:
    st.info(f"📂 **No weekly data found.** Save CSVs in: `{YEAR_FOLDER}/` (e.g., week_01.csv)")
    st.stop()
if not proj_file:
    st.warning("⬅️ **Action Required:** Please upload the projections file in the sidebar.")
    st.stop()

@st.cache_data
def load_and_combine_data(files, proj_f):
    # Projections
    df_proj = pd.read_csv(proj_f)
    df_proj.columns = df_proj.columns.str.lower()
    if 'playerid' in df_proj.columns:
        df_proj['playerid'] = df_proj['playerid'].astype(str)
    
    # Weekly Actuals
    all_weeks = []
    for i, f in enumerate(files):
        temp_df = pd.read_csv(f)
        temp_df.columns = temp_df.columns.str.lower()
        if 'playerid' in temp_df.columns:
            temp_df['playerid'] = temp_df['playerid'].astype(str)
        temp_df['week_num'] = i + 1 
        all_weeks.append(temp_df)
    
    df_actuals = pd.concat(all_weeks, ignore_index=True)
    return df_proj, df_actuals

df_p, df_a = load_and_combine_data(weekly_files, proj_file)

# Core Stats for indexing
if player_type == "Batters":
    core_stats = ['hr', 'sb', 'r', 'rbi', 'avg']
else:
    core_stats = ['w', 'sv', 'so', 'hld', 'era', 'whip']

# --- 4. LEAGUE PULSE (MASTER TABLE) ---
st.header("📡 League Pulse: Waivers & Watchlist")
with st.expander(f"🔍 Scan All {player_type} (Ranked by Heat Index)", expanded=False):
    latest_week_num = df_a['week_num'].max()
    latest_stats = df_a[df_a['week_num'] == latest_week_num]
    
    pulse_data = []
    for _, row in latest_stats.iterrows():
        p_name = row['name']
        p_proj = df_p[df_p['name'] == p_name]
        
        if p_proj.empty: continue
        
        total_delta = 0
        for stat in core_stats:
            if stat in ['era', 'whip', 'avg'] or stat not in row or stat not in p_proj.columns: 
                continue
            
            stat_std = df_p[stat].std() + 1e-9
            weekly_pace = p_proj[stat].values[0] / 26
            
            # Simple Delta: (Actual this week - Weekly Pace) / StdDev
            stat_delta = (row[stat] - weekly_pace) / stat_std
            total_delta += stat_delta
            
        pulse_data.append({
            'Player': p_name, 
            'Team': row.get('team', 'N/A').upper(), 
            'Heat Index': round(total_delta, 2)
        })

    pulse_df = pd.DataFrame(pulse_data).sort_values(by='Heat Index', ascending=False)
    
    st.write("Sort by clicking headers. Use the search icon to find specific waiver wire targets.")
    
    # Styled Master Table with Heatmap
    st.dataframe(
        pulse_df.style.background_gradient(cmap='RdYlGn', subset=['Heat Index']),
        hide_index=True,
        use_container_width=True,
        height=400
    )

st.divider()

# --- 5. FUZZY SEARCH ---
all_players = sorted(df_a['name'].unique())
default_name = "Aaron Judge" if player_type == "Batters" else ""
search_input = st.text_input("Search for a Player (Fuzzy Matching):", value=default_name)

if search_input:
    match, score = process.extractOne(search_input, all_players)
    selected_player = match
    st.success(f"Viewing: **{selected_player}**")
else:
    st.stop()

# --- 6. DATA FILTERING & TREND LOGIC ---
player_actuals = df_a[df_a['name'] == selected_player].sort_values('week_num')
player_proj = df_p[df_p['name'] == selected_player]

if player_proj.empty:
    st.error("Player not found in projections.")
    st.stop()

weeks = player_actuals['week_num'].tolist()

display_options = [s.upper() for s in core_stats if s in df_a.columns]
display_options.insert(0, "COMBINED INDEX") 
stat_to_track = st.radio("Statistic to Track", display_options, horizontal=True).lower()

if stat_to_track == "combined index":
    actual_units = np.zeros(len(weeks))
    expected_units = np.zeros(len(weeks))
    
    for stat in core_stats:
        if stat not in df_a.columns or stat not in df_p.columns or stat in ['era', 'whip', 'avg']: 
            continue
        
        stat_std = df_p[stat].std() + 1e-9
        full_proj = player_proj[stat].values[0]
        weekly_pace = full_proj / 26
        
        actual_cum = player_actuals[stat].cumsum().values / stat_std
        expected_cum = np.array([weekly_pace * w for w in weeks]) / stat_std
            
        actual_units += actual_cum
        expected_units += expected_cum
    
    chart_data = pd.DataFrame({'Week': weeks, 'Actual': actual_units, 'Projected Pace': expected_units})
    y_label = "Standardized Value Units"
else:
    is_rate_stat = stat_to_track in ['era', 'whip', 'avg']
    val_proj = player_proj[stat_to_track].values[0]
    
    if not is_rate_stat:
        weekly_pace = val_proj / 26
        actual_data = player_actuals[stat_to_track].cumsum().tolist()
        expected_data = [weekly_pace * w for w in weeks]
        y_label = f"Cumulative {stat_to_track.upper()}"
    else:
        actual_data = player_actuals[stat_to_track].tolist()
        expected_data = [val_proj] * len(weeks)
        y_label = f"Weekly {stat_to_track.upper()}"

    chart_data = pd.DataFrame({'Week': weeks, 'Actual': actual_data, 'Projected Pace': expected_data})

# --- 7. PLOTLY CHARTING ---
fig = px.line(chart_data, x='Week', y=['Actual', 'Projected Pace'],
              title=f"{selected_player}: {stat_to_track.upper()} Trends",
              labels={'value': y_label, 'variable': 'Legend'},
              markers=True, template="plotly_dark")

fig.update_traces(line=dict(dash='dash', color='orange'), selector=dict(name='Projected Pace'))
fig.update_traces(line=dict(width=4, color='#00d4ff'), selector=dict(name='Actual'))

st.plotly_chart(fig, use_container_width=True)

# Metrics
final_act = chart_data['Actual'].iloc[-1]
final_proj = chart_data['Projected Pace'].iloc[-1]
diff = final_act - final_proj

st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Current Performance", f"{final_act:.2f}")
c2.metric("Projected Pace", f"{final_proj:.2f}")
delta_val = -float(diff) if stat_to_track in ['era', 'whip'] else float(diff)
c3.metric(label="Pace Differential", value=f"{diff:.2f}", delta=delta_val)