import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("MLB Game Outcome Dashboard – August 4, 2025")

# Data
games = [
    {"Date": "2025-08-04", "Team 1": "Giants", "Team 2": "Pirates", "Win % (Team 1)": 63},
    {"Date": "2025-08-04", "Team 1": "Twins", "Team 2": "Tigers", "Win % (Team 1)": 42},
    {"Date": "2025-08-04", "Team 1": "Astros", "Team 2": "Marlins", "Win % (Team 1)": 69},
    {"Date": "2025-08-04", "Team 1": "Orioles", "Team 2": "Phillies", "Win % (Team 1)": 35},
    {"Date": "2025-08-04", "Team 1": "Royals", "Team 2": "Red Sox", "Win % (Team 1)": 47},
]
df = pd.DataFrame(games)

# Table
st.subheader("Projected Outcomes")
st.dataframe(df)

# Chart
st.subheader("Win Probabilities – Team 1")
fig, ax = plt.subplots()
teams = [f"{row['Team 1']} vs {row['Team 2']}" for idx, row in df.iterrows()]
win_probs = df["Win % (Team 1)"]
bars = ax.barh(teams, win_probs, color=['green' if wp > 50 else 'red' for wp in win_probs])
ax.set_xlim(0, 100)
ax.set_xlabel("Win Probability (%)")
ax.set_title("Team 1 Win Probability")
for bar in bars:
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f"{bar.get_width()}%", va='center')
st.pyplot(fig)
