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
    df_proj = pd.read_csv(proj_f)
    df_proj.columns = df_proj.columns.str.lower()
    if 'playerid' in df_proj.columns:
        df_proj['playerid'] = df_proj['playerid'].astype(str)
    
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

# Logic definitions
latest_week_num = df_a['week_num'].max()
prev_week_num = latest_week_num - 1

if player_type == "Batters":
    core_stats = ['hr', 'sb', 'r', 'rbi', 'avg']
    vol_stat = 'pa'
    # Dynamic Threshold: 5 PA per week elapsed
    MIN_VOL_THRESHOLD = 5.0 * latest_week_num
else:
    core_stats = ['w', 'sv', 'so', 'hld', 'era', 'whip']
    vol_stat = 'ip'
    # Dynamic Threshold: 1.0 IP per week elapsed
    MIN_VOL_THRESHOLD = 1.0 * latest_week_num

negative_stats = ['era', 'whip', 'bb', 'cs', 'e', 'l', 'hra']

def calculate_heat_value(stats_row, proj_row, core_list, p_df):
    h = 0
    for s in core_list:
        if s not in stats_row or s not in proj_row.columns: continue
        std = p_df[s].std() + 1e-9
        pace = proj_row[s].values[0] / 26
        diff = stats_row[s] - pace
        h += -(diff)/std if s.lower() in negative_stats else diff/std
    return h

# --- 4. LEAGUE PULSE ---
st.header("📡 League Pulse: Momentum & Waivers")
with st.expander(f"🔍 Scan All {player_type} (Ranked by Velocity)", expanded=False):
    latest_stats = df_a[df_a['week_num'] == latest_week_num]
    has_prev = prev_week_num in df_a['week_num'].unique()
    
    pulse_data = []
    for _, row in latest_stats.iterrows():
        p_name = row['name']
        p_proj = df_p[df_p['name'] == p_name]
        if p_proj.empty or row.get(vol_stat, 0) < MIN_VOL_THRESHOLD:
            continue
        
        curr_heat = calculate_heat_value(row, p_proj, core_stats, df_p)
        velocity = 0
        if has_prev:
            prev_row = df_a[(df_a['name'] == p_name) & (df_a['week_num'] == prev_week_num)]
            if not prev_row.empty:
                velocity = curr_heat - calculate_heat_value(prev_row.iloc[0], p_proj, core_stats, df_p)

        pulse_data.append({
            'Player': p_name, 
            'Team': row.get('team', 'N/A').upper(), 
            vol_stat.upper(): row.get(vol_stat, 0),
            'Heat Index': round(curr_heat, 2),
            'Velocity': round(velocity, 2) if has_prev else 0.0
        })

    if pulse_data:
        pulse_df = pd.DataFrame(pulse_data).sort_values(by='Velocity' if has_prev else 'Heat Index', ascending=False)
        st.dataframe(
            pulse_df.style.background_gradient(cmap='RdYlGn', subset=['Heat Index'], vmin=-2, vmax=2)
                          .background_gradient(cmap='PuOr', subset=['Velocity'], vmin=-1, vmax=1),
            hide_index=True, use_container_width=True, height=350
        )
    else:
        st.warning(f"No players met volume threshold ({MIN_VOL_THRESHOLD} {vol_stat.upper()}).")

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

# --- 6. DATA FILTERING ---
player_actuals = df_a[df_a['name'] == selected_player].sort_values('week_num')
player_proj = df_p[df_p['name'] == selected_player]

if player_proj.empty:
    st.error("Player not found in projections.")
    st.stop()

weeks = player_actuals['week_num'].tolist()
available_core = [s for s in core_stats if s in df_a.columns]
display_options = [s.upper() for s in available_core]
display_options.insert(0, "COMBINED INDEX") 
stat_to_track = st.radio("Statistic to Track", display_options, horizontal=True).lower()

# --- 7. TREND LOGIC & CHARTS ---
st.info("""
💡 **Guide:** * **Cumulative Performance:** Blue vs Orange shows if they are hitting their year-end pace. 
* **Weekly Momentum:** Shows 'Heat' per week. **Positive (Green)** is beating pace. **Velocity** is the change between bars.
""")

col_chart1, col_chart2 = st.columns(2)

# Chart 1: Performance vs Pace
if stat_to_track == "combined index":
    actual_units = np.zeros(len(weeks))
    expected_units = np.zeros(len(weeks))
    for stat in available_core:
        if stat not in df_p.columns or stat in ['era', 'whip', 'avg']: continue
        stat_std = df_p[stat].std() + 1e-9
        full_proj = player_proj[stat].values[0]
        weekly_pace = full_proj / 26
        actual_units += player_actuals[stat].cumsum().values / stat_std
        expected_units += np.array([weekly_pace * w for w in weeks]) / stat_std
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

with col_chart1:
    fig_main = px.line(chart_data, x='Week', y=['Actual', 'Projected Pace'],
                  title=f"📈 {selected_player}: {stat_to_track.upper()} Performance",
                  labels={'value': y_label, 'variable': 'Legend'},
                  markers=True, template="plotly_dark")
    fig_main.update_traces(line=dict(dash='dash', color='orange'), selector=dict(name='Projected Pace'))
    fig_main.update_traces(line=dict(width=4, color='#00d4ff'), selector=dict(name='Actual'))
    st.plotly_chart(fig_main, use_container_width=True)

# Chart 2: Weekly Momentum
weekly_heats = [calculate_heat_value(row, player_proj, core_stats, df_p) for _, row in player_actuals.iterrows()]
momentum_df = pd.DataFrame({'Week': weeks, 'Weekly Heat': weekly_heats})
momentum_df['Velocity'] = momentum_df['Weekly Heat'].diff().fillna(0)

with col_chart2:
    fig_mom = px.bar(momentum_df, x='Week', y='Weekly Heat', 
                     title=f"🔥 {selected_player}: Weekly Momentum (Heat Index)",
                     color='Weekly Heat', color_continuous_scale='RdYlGn', 
                     color_continuous_midpoint=0, template="plotly_dark")
    st.plotly_chart(fig_mom, use_container_width=True)

# --- 8. BREAKDOWN TABLE ---
st.subheader(f"📊 {selected_player}: Detailed Breakdown")

valid_table_cols = ['week_num']
if vol_stat in player_actuals.columns: valid_table_cols.append(vol_stat)
for s in available_core:
    valid_table_cols.append(s)

breakdown_df = player_actuals[valid_table_cols].copy()
breakdown_df['WEEKLY_HEAT'] = [round(h, 2) for h in weekly_heats]
breakdown_df['VELOCITY'] = [round(v, 2) for v in momentum_df['Velocity'].tolist()]

for s in available_core:
    if s not in ['era', 'whip', 'avg']:
        breakdown_df[f"{s.upper()}_CUM"] = breakdown_df[s].cumsum()

breakdown_df.columns = [c.upper() for c in breakdown_df.columns]
st.dataframe(breakdown_df, hide_index=True, use_container_width=True)

# Footer Metrics
final_act = chart_data['Actual'].iloc[-1]
final_proj = chart_data['Projected Pace'].iloc[-1]
diff = final_act - final_proj
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Current Performance", f"{final_act:.2f}")
c2.metric("Projected Pace", f"{final_proj:.2f}")
delta_val = -float(diff) if stat_to_track in negative_stats else float(diff)
c3.metric(label="Pace Differential", value=f"{diff:.2f}", delta=delta_val)