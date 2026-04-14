import streamlit as st

st.set_page_config(page_title="Fantasy Analytics Home", page_icon="⚾", layout="wide")

st.title("⚾ Fantasy Baseball Analytics Suite")

st.markdown("""
Welcome to your custom analytical dashboard. Use the sidebar on the left to navigate between tools:

### 1. 📊 System Evaluator
Compare pre-season projection systems (ZiPS, Steamer, etc.) against actual results to see which is most accurate for your league settings.

### 2. 📈 Roster Trends
Track individual player performance against their projected pace. Includes the **League Pulse** to find hot waiver wire targets and acceleration (velocity) metrics.

### 3. 🧪 Research Lab
Perform deep-dive statistical analysis. Use the **Correlation Matrix** to find relationships between raw metrics (like Bat Speed) and fantasy outcomes.
""")

st.divider()
st.info("💡 **Pro Tip:** New weekly data dropped into the `data/weekly_stats/` folders will automatically update the Trends and Research Lab pages.")