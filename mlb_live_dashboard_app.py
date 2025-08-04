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

# Streamlit setup
st.set_page_config(page_title="MLB Forecast Dashboard", layout="wide")
st.title("⚾ MLB Win Probability Dashboard – 2025 Season")
st.sidebar.header("Filter Games")
selected_date = st.sidebar.date_input("Select Date", date.today())

# Fetch data
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
        elif response.status_code == 401 and "OUT_OF_USAGE_CREDITS" in response.text:
            st.error("⚠️ You’ve reached your API quota. Upgrade your plan or wait for reset.")
            return []
        else:
            st.error(f"API error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return []

# Parse data
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

# Run
odds_data = fetch_live_odds()
df = parse_odds_data(odds_data)

if df.empty:
    st.warning("No valid games available from the API.")
    st.stop()

# Convert date strings to actual datetime for accurate filtering
df["Date"] = pd.to_datetime(df["Date"])
selected_date = pd.to_datetime(selected_date)

df_filtered = df[df["Date"].dt.date == selected_date.date()]

st.subheader(f"Games on {selected_date.date()}")
st.dataframe(df_filtered)

if not df_filtered.empty:
    st.subheader("📊 Home Team Win Probabilities")
    fig = px.bar(
        df_filtered,
        x="Win % (Home)",
        y="Home Team",
        orientation="h",
        color="Win % (Home)",
        color_continuous_scale="RdYlGn",
        labels={"Win % (Home)": "Home Win Probability (%)"},
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)
# Fetch & parse
odds_data = fetch_live_odds()

if not odds_data:
    st.warning("⚠️ No raw data returned from the API.")
    st.stop()

df = parse_odds_data(odds_data)

# Debug: Show parsed raw DataFrame
st.subheader("🔍 Parsed Data")
st.write(df)

if df.empty:
    st.warning("⚠️ Parsed DataFrame is empty after processing.")
    st.stop()

# Fix date filtering
df["Date"] = pd.to_datetime(df["Date"])
selected_date = pd.to_datetime(selected_date)

st.info(f"📅 Selected date: {selected_date.date()}")
st.info(f"📅 Dates in data: {df['Date'].dt.date.unique().tolist()}")

df_filtered = df[df["Date"].dt.date == selected_date.date()]

# Display filtered games
st.subheader(f"🎯 Games on {selected_date.date()}")
st.dataframe(df_filtered)

if df_filtered.empty:
    st.warning("🚫 No games match the selected date.")
    st.stop()

# Plot
st.subheader("📊 Home Team Win Probabilities")
fig = px.bar(
    df_filtered,
    x="Win % (Home)",
    y="Home Team",
    orientation="h",
    color="Win % (Home)",
    color_continuous_scale="RdYlGn",
    labels={"Win % (Home)": "Home Win Probability (%)"},
    height=600
)
st.plotly_chart(fig, use_container_width=True)
