# Fantasy Baseball Analytics & Trend Tracker

A custom-built Streamlit analytical suite designed to evaluate baseball projection systems (ZiPS, Steamer, etc.) and track player performance trends relative to pre-season pace.

## 🚀 Features

### 1. System Evaluator (`evaluator.py`)
- **Head-to-Head Comparison:** Upload multiple projection CSVs (e.g., ZiPS and Steamer) and compare them against actual year-end results.
- **Scaled Error Index:** Normalizes misses across different categories (Home Runs vs. Strikeouts) using Standard Deviation scaling to identify which system is mathematically more accurate.
- **WAPE Metric:** Provides a "Weighted Absolute Percentage Error" for a human-readable high-level accuracy percentage.
- **Automated Verdicts:** Instantly identifies the "winning" system based on your selected categories.

### 2. Roster Trends & Pace Tracker (`trends.py`)
- **Fuzzy Matching Search:** Easily find players with nicknames or complex spellings (e.g., typing "Vlad" finds "Vladimir Guerrero Jr.").
- **Pace vs. Actual Charting:** Visualize a player's cumulative performance against a linear "Expected Pace" baseline derived from their full-season projection.
- **Combined Performance Index:** A proprietary trend line that aggregates performance across all core fantasy categories into a single "Value Unit" graph.
- **Rate Stat Support:** Specialized logic for ERA, WHIP, and AVG that tracks weekly snapshots against season-long targets.

## 📁 Project Structure

```text
fantasy-baseball-ranking/
├── app/
│   ├── Home.py              # Main navigation entry point
│   └── pages/
│       ├── evaluator.py     # System accuracy analytics
│       └── trends.py        # Player performance tracking
├── data/
│   └── weekly_stats/        # Automated "Drop Folder" for weekly exports
│       └── 2026/
│           ├── batters/     # Weekly Hitter CSVs
│           └── pitchers/    # Weekly Pitcher CSVs
├── venv/                    # Virtual environment
└── requirements.txt         # Project dependencies
