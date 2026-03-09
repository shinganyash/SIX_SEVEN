import streamlit as st
import plotly.express as px
import pandas as pd
import json
from utils.data_processing import data

st.set_page_config(layout="wide")

st.title("Crimes Against Women in India")
st.write("Dashboard by Yash Shingan")

# --------------------------------------------------
# Crime columns
# --------------------------------------------------

crime_cols = [
    "Rape",
    "Kidnap and assault",
    "Dowry deaths",
    "Assault on women",
    "Assault on modesty",
    "Domestic violence",
    "Women trafficking"
]

# --------------------------------------------------
# Clean numeric columns
# --------------------------------------------------

data["Population"] = (
    data["Population"]
    .astype(str)
    .str.replace(",", "")
    .astype(float)
)

data[crime_cols] = data[crime_cols].apply(pd.to_numeric, errors="coerce")

data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
data = data.dropna(subset=["Year"])
data["Year"] = data["Year"].astype(int)

# --------------------------------------------------
# Create total crimes + crime rate
# --------------------------------------------------

data["Total Crimes"] = data[crime_cols].sum(axis=1)

data["Crime Rate"] = (data["Total Crimes"] / data["Population"]) * 100000

data = data.sort_values("Year")

# --------------------------------------------------
# STATE TREND CHART
# --------------------------------------------------

st.header("Crime Trends Over Time")

state = st.selectbox("Choose a state", sorted(data["State"].unique()))

state_df = data[data["State"] == state]

fig_line = px.line(
    state_df,
    x="Year",
    y=crime_cols,
    labels={"value": "Number of Cases"}
)

st.plotly_chart(fig_line, use_container_width=True)

# --------------------------------------------------
# CRIME MAP
# --------------------------------------------------

st.header("Crime Map of India")

crime_choice = st.selectbox(
    "Select crime type",
    crime_cols + ["Total Crimes"]
)

# rate for selected crime
data["Selected Crime Rate"] = (data[crime_choice] / data["Population"]) * 100000

# --------------------------------------------------
# Load geojson
# --------------------------------------------------

with open("india_states.geojson") as f:
    geojson = json.load(f)

# --------------------------------------------------
# Animated choropleth
# --------------------------------------------------

fig_map = px.choropleth(
    data,
    geojson=geojson,
    locations="State",
    featureidkey="properties.ST_NM",
    color="Selected Crime Rate",
    animation_frame="Year",
    color_continuous_scale="Reds",
    title=f"{crime_choice} Rate per 100k People"
)

fig_map.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig_map, use_container_width=True)

# --------------------------------------------------
# MOST DANGEROUS STATES LEADERBOARD
# --------------------------------------------------

st.header("Top 10 States with Highest Crime Rate")

year_choice = st.slider(
    "Select year",
    int(data["Year"].min()),
    int(data["Year"].max()),
    int(data["Year"].max())
)

year_df = data[data["Year"] == year_choice]

year_df["Rate"] = (year_df[crime_choice] / year_df["Population"]) * 100000

top_states = (
    year_df[["State", "Rate"]]
    .sort_values("Rate", ascending=False)
    .head(10)
)

fig_bar = px.bar(
    top_states,
    x="Rate",
    y="State",
    orientation="h",
    title=f"Top 10 States ({year_choice})",
    labels={"Rate": "Crimes per 100k people"}
)

st.plotly_chart(fig_bar, use_container_width=True)