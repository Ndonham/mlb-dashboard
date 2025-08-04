import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import date

# CONFIG
st.set_page_config(page_title="MLB Forecast Dashboard", layout="wide")
st.title("⚾ MLB Win Probability Dashboard – 2025 Season")
st.sidebar.header("Filter Games")
selected_date = st.sidebar.date_input("Select Date", date.today())

# API CONFIG – replace this with your real key
API_KEY = "d9cb26de03b65a0537bff3e5cafdcf45"
BASE_URL = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"

def fetch_live_odds():
    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "h2h",
        "dateFormat": "iso"
    }
    try:
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return []

def parse_odds_data(data):
    rows = []
    for event in data:
        try:
            if "bookmakers" not in event or not event["bookmakers"]:
                continue
            bookmaker = event["bookmakers"][0]
            if "markets" not in bookmaker or not bookmaker["markets"]:
                continue
            outcomes = bookmaker["markets"][0]["outcomes"]
            if len(outcomes) < 2:
                continue

            home_team = event.get("home_team", "Unknown")
            teams = event.get("teams")
            if not teams or not isinstance(teams, list) or len(teams) < 2 or home_team not in teams:
                continue

            away_team = teams[1] if teams[0] == home_team else teams[0]

            price_home = next((o["price"] for o in outcomes if o["name"] == home_team), None)
            price_away = next((o["price"] for o in outcomes if o["name"] == away_team), None)

            if price_home is None or price_away is None:
                continue

            prob_home = round(100 * (1 / price_home) / ((1 / price_home) + (1 / price_away)), 1)
            prob_away = round(100 * (1 / price_away) / ((1 / price_home) + (1 / price_away)), 1)

            row = {
                "Date": event["commence_time"][:10],
                "Home Team": home_team,
                "Away Team": away_team,
                "Win % (Home)": prob_home,
                "Win % (Away)": prob_away
            }
            rows.append(row)
        except Exception as e:
            print(f"Skipping event due to error: {e}")
            continue
    return pd.DataFrame(rows)

# FETCH AND PARSE DATA
odds_data = fetch_live_odds()
df = parse_odds_data(odds_data)

if "Date" not in df.columns or df.empty:
    st.warning("No valid games available from the API.")
    st.stop()

df_filtered = df[df["Date"] == selected_date.strftime("%Y-%m-%d")]
st.subheader(f"Games on {selected_date}")
st.dataframe(df_filtered)

if not df_filtered.empty:
    st.subheader("📊 Home Team Win Probabilities")
    fig = px.bar(df_filtered, x="Win % (Home)", y="Home Team", orientation="h",
                 color="Win % (Home)", color_continuous_scale="RdYlGn",
                 labels={"Win % (Home)": "Home Win Probability (%)"},
                 height=600)
    st.plotly_chart(fig, use_container_width=True)
