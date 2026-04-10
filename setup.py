import os

# Define the directory structure
directories = [
    "fantasy-baseball-rating/config",
    "fantasy-baseball-rating/data/raw",
    "fantasy-baseball-rating/data/sample",
    "fantasy-baseball-rating/notebooks",
    "fantasy-baseball-rating/src",
    "fantasy-baseball-rating/app/pages",
    "fantasy-baseball-rating/tests",
    "fantasy-baseball-rating/deploy"
]

# Define the files to create
files = [
    "fantasy-baseball-rating/.gitignore",
    "fantasy-baseball-rating/README.md",
    "fantasy-baseball-rating/requirements.txt",
    "fantasy-baseball-rating/config/leagues.yaml",
    "fantasy-baseball-rating/notebooks/01_data_exploration.ipynb",
    "fantasy-baseball-rating/src/__init__.py",
    "fantasy-baseball-rating/src/scoring.py",
    "fantasy-baseball-rating/src/evaluator.py",
    "fantasy-baseball-rating/src/tracker.py",
    "fantasy-baseball-rating/app/Home.py",
    "fantasy-baseball-rating/app/pages/1_League_Rules.py",
    "fantasy-baseball-rating/app/pages/2_System_Evaluator.py",
    "fantasy-baseball-rating/app/pages/3_Roster_Trends.py",
    "fantasy-baseball-rating/tests/test_scoring.py",
    "fantasy-baseball-rating/deploy/Dockerfile"
]

# Create directories
for d in directories:
    os.makedirs(d, exist_ok=True)

# Create empty files
for f in files:
    with open(f, 'w') as file:
        pass

print("Git repository structure created successfully in the 'fantasy-baseball-rating' folder!")
