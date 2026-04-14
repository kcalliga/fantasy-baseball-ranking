import streamlit as st

# Define the individual pages
# The first argument is the file path, the second is the display name in the menu
rules_page = st.Page("pages/rules.py", title="League Rules", icon="⚙️")
evaluator_page = st.Page("pages/evaluator.py", title="System Evaluator", icon="⚖️")
draft_page = st.Page("pages/draft.py", title="Draft Board & Valuation", icon="📋")
trends_page = st.Page("pages/trends.py", title="Roster Trends", icon="📈")

# Group the pages into categorized sections
pg = st.navigation({
    "Setup": [rules_page],
    "1. Pre-Season": [evaluator_page],
    "2. Draft Time": [draft_page],
    "3. In-Season": [trends_page]
})

# Configure the main page layout once for the whole app
st.set_page_config(page_title="Fantasy Baseball Tracker", page_icon="⚾", layout="wide")

# Run the navigation router
pg.run()
