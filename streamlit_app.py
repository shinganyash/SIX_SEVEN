import streamlit as st
import plotly.express as px
import pandas as pd
import json
from utils.data_processing import data

st.set_page_config(layout="wide")

st.title("Crimes Against Women in India")
st.write("Dashboard by Yash Shingan")

# ------------------------------------------------
# Crime columns
# ------------------------------------------------

crime_cols = [
    "Rape",
    "Kidnap and assault",
    "Dowry deaths",
    "Assault on women",
    "Assault on modesty",
    "Domestic violence",
    "Women trafficking"
]

# ------------------------------------------------
# Clean numeric columns
# ------------------------------------------------

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

# ------------------------------------------------
# Create totals and crime rate
# ------------------------------------------------

data["Total Crimes"] = data[crime_cols].sum(axis=1)

data["Crime Rate"] = (data["Total Crimes"] / data["Population"]) * 100000

data = data.sort_values("Year")

# ------------------------------------------------
# KEY INSIGHTS
# ------------------------------------------------

st.header("Key Insights")

latest_year = data["Year"].max()
latest_df = data[data["Year"] == latest_year].copy()

latest_df["Rate"] = (latest_df["Total Crimes"] / latest_df["Population"]) * 100000

most_dangerous = latest_df.sort_values("Rate", ascending=False).iloc[0]
safest = latest_df.sort_values("Rate").iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric("Total Crimes (Latest Year)", int(latest_df["Total Crimes"].sum()))

col2.metric(
    "Most Dangerous State",
    most_dangerous["State"],
    f"{most_dangerous['Rate']:.2f} per 100k"
)

col3.metric(
    "Safest State",
    safest["State"],
    f"{safest['Rate']:.2f} per 100k"
)

# ------------------------------------------------
# STATE CRIME TRENDS
# ------------------------------------------------

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

# ------------------------------------------------
# CRIME MAP
# ------------------------------------------------

st.header("Crime Map of India")

crime_choice = st.selectbox(
    "Select crime type",
    crime_cols + ["Total Crimes"]
)

data["Selected Crime Rate"] = (data[crime_choice] / data["Population"]) * 100000

with open("india_states.geojson") as f:
    geojson = json.load(f)

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

# ------------------------------------------------
# TOP 10 DANGEROUS STATES
# ------------------------------------------------

st.header("Top 10 States with Highest Crime Rate")

year_choice = st.slider(
    "Select year",
    int(data["Year"].min()),
    int(data["Year"].max()),
    int(data["Year"].max())
)

year_df = data[data["Year"] == year_choice].copy()

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

# ------------------------------------------------
# COMPARE TWO STATES
# ------------------------------------------------

st.header("Compare Two States")

col1, col2 = st.columns(2)

state1 = col1.selectbox("State 1", sorted(data["State"].unique()))
state2 = col2.selectbox("State 2", sorted(data["State"].unique()), index=1)

compare_df = data[data["State"].isin([state1, state2])]

fig_compare = px.line(
    compare_df,
    x="Year",
    y="Total Crimes",
    color="State",
    title="Crime Comparison Between States"
)

st.plotly_chart(fig_compare, use_container_width=True)

# ------------------------------------------------
# CRIME CHANGE SINCE 2001
# ------------------------------------------------

st.header("Crime Change Since 2001")

start_year = data["Year"].min()
end_year = data["Year"].max()

start_df = data[data["Year"] == start_year][["State", "Crime Rate"]]
end_df = data[data["Year"] == end_year][["State", "Crime Rate"]]

change_df = start_df.merge(end_df, on="State", suffixes=("_start", "_end"))

change_df["Change"] = change_df["Crime Rate_end"] - change_df["Crime Rate_start"]

fig_change = px.choropleth(
    change_df,
    geojson=geojson,
    locations="State",
    featureidkey="properties.ST_NM",
    color="Change",
    color_continuous_scale="RdBu",
    title="Change in Crime Rate Since 2001"
)

fig_change.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig_change, use_container_width=True)

# ------------------------------------------------
# DATASET VIEWER
# ------------------------------------------------

st.header("Dataset")

if st.checkbox("Show raw data"):
    st.dataframe(data)