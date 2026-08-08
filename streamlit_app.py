# -*- coding: utf-8 -*-
from datetime import datetime
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(
    page_title="Patna Weather",
    page_icon="🌦️",
    layout="wide",
)

# Fetch Patna Weather Data from Open-Meteo Historical Weather API
@st.cache_data
def load_patna_weather_data():
    url = (
        "https://archive-api.open-meteo.com/v1/archive?"
        "latitude=25.5941&longitude=85.1376&"
        "start_date=2021-01-01&end_date=2025-12-31&"
        "daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weather_code&"
        "timezone=Asia%2FKolkata"
    )
    df = pd.read_json(url)["daily"]
    df = pd.DataFrame(df)
    df["date"] = pd.to_datetime(df["time"])
    
    # Rename columns to match the original schema
    df = df.rename(columns={
        "temperature_2m_max": "temp_max",
        "temperature_2m_min": "temp_min",
        "precipitation_sum": "precipitation",
        "wind_speed_10m_max": "wind"
    })

    # Simple weather category mapping from WMO weather codes
    def map_weather(code):
        if code in [0, 1]:
            return "sun"
        elif code in [2, 3]:
            return "fog"
        elif code in [51, 53, 55, 61, 63, 65, 80, 81]:
            return "rain"
        elif code in [71, 73, 75]:
            return "snow"
        else:
            return "drizzle"

    df["weather"] = df["weather_code"].apply(map_weather)
    return df

full_df = load_patna_weather_data()

"""
# Patna Weather

Explore daily weather data for Patna, Bihar!
"""

""

"""
## Recent Year Summary (2025 vs 2024)
"""

""

df_2025 = full_df[full_df["date"].dt.year == 2025]
df_2024 = full_df[full_df["date"].dt.year == 2024]

max_temp_2025 = df_2025["temp_max"].max()
max_temp_2024 = df_2024["temp_max"].max()

min_temp_2025 = df_2025["temp_min"].min()
min_temp_2024 = df_2024["temp_min"].min()

max_wind_2025 = df_2025["wind"].max()
max_wind_2024 = df_2024["wind"].max()

min_wind_2025 = df_2025["wind"].min()
min_wind_2024 = df_2024["wind"].min()

max_prec_2025 = df_2025["precipitation"].max()
max_prec_2024 = df_2024["precipitation"].max()

min_prec_2025 = df_2025["precipitation"].min()
min_prec_2024 = df_2024["precipitation"].min()

cols = st.columns(4, gap="medium")

with cols[0]:
    st.metric(
        "Max Temperature",
        f"{max_temp_2025:0.1f}°C",
        delta=f"{max_temp_2025 - max_temp_2024:0.1f}°C",
    )
    st.metric(
        "Min Temperature",
        f"{min_temp_2025:0.1f}°C",
        delta=f"{min_temp_2025 - min_temp_2024:0.1f}°C",
    )

with cols[1]:
    st.metric(
        "Max Precipitation",
        f"{max_prec_2025:0.1f} mm",
        delta=f"{max_prec_2025 - max_prec_2024:0.1f} mm",
    )
    st.metric(
        "Min Precipitation",
        f"{min_prec_2025:0.1f} mm",
        delta=f"{min_prec_2025 - min_prec_2024:0.1f} mm",
    )

with cols[2]:
    st.metric(
        "Max Wind Speed",
        f"{max_wind_2025:0.1f} km/h",
        delta=f"{max_wind_2025 - max_wind_2024:0.1f} km/h",
    )
    st.metric(
        "Min Wind Speed",
        f"{min_wind_2025:0.1f} km/h",
        delta=f"{min_wind_2025 - min_wind_2024:0.1f} km/h",
    )

weather_icons = {
    "sun": "☀️",
    "snow": "☃️",
    "rain": "💧",
    "fog": "😶‍🌫️",
    "drizzle": "🌧️",
}

with cols[3]:
    weather_most = (
        full_df["weather"].value_counts().head(1).reset_index()["weather"][0]
    )
    st.metric(
        "Most Common Weather",
        f"{weather_icons.get(weather_most, '☀️')} {weather_most.upper()}",
    )

    weather_least = (
        full_df["weather"].value_counts().tail(1).reset_index()["weather"][0]
    )
    st.metric(
        "Least Common Weather",
        f"{weather_icons.get(weather_least, '🌫️')} {weather_least.upper()}",
    )

""
""

"""
## Compare Different Years
"""

YEARS = full_df["date"].dt.year.unique()
selected_years = st.pills(
    "Years to compare", YEARS, default=YEARS, selection_mode="multi"
)

if not selected_years:
    st.warning("You must select at least 1 year.", icon=":material/warning:")

df = full_df[full_df["date"].dt.year.isin(selected_years)]

cols = st.columns([3, 1])

with cols[0].container(border=True, height="stretch"):
    "### Temperature"

    st.altair_chart(
        alt.Chart(df)
        .mark_bar(width=1)
        .encode(
            alt.X("date", timeUnit="monthdate").title("Date"),
            alt.Y("temp_max").title("Temperature Range (°C)"),
            alt.Y2("temp_min"),
            alt.Color("date:N", timeUnit="year").title("Year"),
            alt.XOffset("date:N", timeUnit="year"),
        )
        .configure_legend(orient="bottom"),
        use_container_width=True
    )

with cols[1].container(border=True, height="stretch"):
    "### Weather Distribution"

    st.altair_chart(
        alt.Chart(df)
        .mark_arc()
        .encode(
            alt.Theta("count()"),
            alt.Color("weather:N"),
        )
        .configure_legend(orient="bottom"),
        use_container_width=True
    )

cols = st.columns(2)

with cols[0].container(border=True, height="stretch"):
    "### Wind"

    st.altair_chart(
        alt.Chart(df)
        .transform_window(
            avg_wind="mean(wind)",
            std_wind="stdev(wind)",
            frame=[0, 14],
            groupby=["monthdate(date)"],
        )
        .mark_line(size=1)
        .encode(
            alt.X("date", timeUnit="monthdate").title("Date"),
            alt.Y("avg_wind:Q").title("Average Wind Past 2 Weeks (km/h)"),
            alt.Color("date:N", timeUnit="year").title("Year"),
        )
        .configure_legend(orient="bottom"),
        use_container_width=True
    )

with cols[1].container(border=True, height="stretch"):
    "### Precipitation"

    st.altair_chart(
        alt.Chart(df)
        .mark_bar()
        .encode(
            alt.X("date:N", timeUnit="month").title("Date"),
            alt.Y("precipitation:Q").aggregate("sum").title("Precipitation (mm)"),
            alt.Color("date:N", timeUnit="year").title("Year"),
        )
        .configure_legend(orient="bottom"),
        use_container_width=True
    )

cols = st.columns(2)

with cols[0].container(border=True, height="stretch"):
    "### Monthly Weather Breakdown"
    ""

    st.altair_chart(
        alt.Chart(df)
        .mark_bar()
        .encode(
            alt.X("month(date):O", title="Month"),
            alt.Y("count():Q", title="Days").stack("normalize"),
            alt.Color("weather:N"),
        )
        .configure_legend(orient="bottom"),
        use_container_width=True
    )

with cols[1].container(border=True, height="stretch"):
    "### Raw Data"

    st.dataframe(df)
