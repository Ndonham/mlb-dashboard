import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import date, timedelta

# CONFIG
st.set_page_config(page_title="MLB Forecast Dashboard", layout="wide")

# APP TITLE
st.title("⚾ MLB Win Probability Dashboard – 2025 Season")

# SIDEBAR CONFIGURATION
st.sidebar.header("Filter Games")
selected_date = st.sidebar.date_input("Select Date", date.today())

# API CONFIG – using user-provided key
API_KEY = "d9cb26de03b65a0537bff3e5cafdcf45"
BASE_URL = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"

def fetch_live_odds():
    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "h2h",
        "dateFormat": "iso"
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("API request failed. Check your key or quota.")
        return []

# PROCESS AND DISPLAY
def parse_odds_data(data):
    rows = []
    for event in data:
        if "bookmakers" not in event or len(event["bookmakers"]) == 0:
            continue
        teams = event["teams"]
        home = event["home_team"]
        bookmaker = event["bookmakers"][0]
        outcomes = bookmaker["markets"][0]["outcomes"]
        row = {
            "Date": event["commence_time"][:10],
            "Team 1": outcomes[0]["name"],
            "Team 2": outcomes[1]["name"],
            "Win % (Team 1)": round(100 * (1 / outcomes[0]["price"]) / ((1 / outcomes[0]["price"]) + (1 / outcomes[1]["price"])), 1),
            "Win % (Team 2)": round(100 * (1 / outcomes[1]["price"]) / ((1 / outcomes[0]["price"]) + (1 / outcomes[1]["price"])), 1),
        }
        rows.append(row)
    return pd.DataFrame(rows)

# FETCH DATA
odds_data = fetch_live_odds()
if odds_data:
    df = parse_odds_data(odds_data)
    df_filtered = df[df["Date"] == selected_date.strftime("%Y-%m-%d")]
    st.subheader(f"Games on {selected_date}")
    st.dataframe(df_filtered)

    # PLOT CHARTS
    st.subheader("📊 Win Probability Chart")
    if not df_filtered.empty:
        fig = px.bar(df_filtered, x="Win % (Team 1)", y="Team 1", orientation="h",
                     color="Win % (Team 1)", color_continuous_scale="RdYlGn",
                     labels={"Win % (Team 1)": "Win Probability (%)", "Team 1": "Matchup"},
                     height=600)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available for the selected date.")
