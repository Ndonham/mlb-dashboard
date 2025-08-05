
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import date
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"

st.set_page_config(page_title="MLB Forecast Dashboard", layout="wide")
st.title("⚾ MLB Win Probability Dashboard – 2025 Season")
st.sidebar.header("🗓️ Filter Games")
selected_date = st.sidebar.date_input("Select Date", date.today())

@st.cache_data
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
            home_team = event["home_team"]
            away_team = event["away_team"]
            game_date = event["commence_time"][:10]

            if not event["bookmakers"]:
                continue
            bookmaker = event["bookmakers"][0]

            if not bookmaker["markets"]:
                continue
            outcomes = bookmaker["markets"][0]["outcomes"]

            prices = {o["name"]: o["price"] for o in outcomes}
            if home_team not in prices or away_team not in prices:
                continue

            price_home = prices[home_team]
            price_away = prices[away_team]

            prob_home = round(100 * (1 / price_home) / ((1 / price_home) + (1 / price_away)), 1)
            prob_away = round(100 * (1 / price_away) / ((1 / price_home) + (1 / price_away)), 1)

            rows.append({
                "Date": game_date,
                "Home Team": home_team,
                "Away Team": away_team,
                "Win % (Home)": prob_home,
                "Win % (Away)": prob_away
            })
        except Exception as e:
            continue
    return pd.DataFrame(rows)

raw_odds = fetch_live_odds()
parsed_df = parse_odds_data(raw_odds)

if parsed_df.empty:
    st.warning("⚠️ Parsed DataFrame is empty after processing.")
    st.stop()

parsed_df["Date"] = pd.to_datetime(parsed_df["Date"])
selected_date = pd.to_datetime(selected_date)
df_filtered = parsed_df[parsed_df["Date"].dt.date == selected_date.date()]

if df_filtered.empty:
    st.warning(f"🚫 No games found for {selected_date.date()}. Try another date.")
    st.stop()

st.subheader(f"📋 Game Summary for {selected_date.strftime('%B %d, %Y')}")
st.dataframe(df_filtered, use_container_width=True)

st.subheader("📊 Home Team Win Probabilities")
fig = px.bar(
    df_filtered,
    x="Win % (Home)",
    y="Home Team",
    orientation="h",
    color="Win % (Home)",
    color_continuous_scale="RdYlGn",
    labels={"Win % (Home)": "Home Win Probability (%)"},
    height=400
)
st.plotly_chart(fig, use_container_width=True)
