import json
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
from collections import defaultdict


st.set_page_config(page_title="SmartPack", page_icon="⛺", layout="centered")

st.title("⛺ SmartPack: Camping Forecast")
st.markdown("Enter a park name to see the forecast and generated gear checklist.")


@st.cache_data
def load_weekly_data():
    with open("weekly_forecasts.json", "r") as f:
        return json.load(f)


data = load_weekly_data()

# All park names -> dropdown list
park_names = list(data.keys())


# Dropdown for parks

selected_park = st.selectbox("Choose a California National Park:", park_names)
park_info = data[selected_park]
forecast = park_info["forecast"]
warnings = park_info["warnings"]
gear = park_info["recommended_gear"]


# Weather Summary Dashboard
st.caption(f"Coordinates: {park_info['latitude']:.2f}, {park_info['longitude']:.2f}")


daily_data = defaultdict(list)

for p in forecast:
    date = p["startTime"].split("T")[0]  # YYYY-MM-DD
    daily_data[date].append(p)

available_dates = sorted(daily_data.keys())

selected_date = st.selectbox("Select forecast date:", available_dates)

day_forecast = daily_data[selected_date]

temps = [p["Temp"] for p in day_forecast if p["Temp"] is not None]
winds = [
    float(p["Wind"].replace("-", "0").split()[0])
    for p in day_forecast
    if p["Wind"] is not None
]
rains = [p["Rain"] or 0 for p in day_forecast]

Det_forecast = [p["detailedForecast"] or 0 for p in day_forecast]

min_temp = min(temps)
max_temp = max(temps)
max_wind = max(winds)
total_rain = sum(rains)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Low Temp", f"{min_temp:.1f} °F")

with col2:
    st.metric("High Temp", f"{max_temp:.1f} °F")

with col3:
    st.metric("Max Wind", f"{max_wind:.1f} mph")

with col4:
    st.metric("Total Rain", f"{total_rain:.1f} mm")

# Gear Recommendations

st.divider()
st.subheader("🎒 Smart Gear Checklist")

# Display warnings
for w in warnings:
    st.error(f"⚠️ {w}")

# Display gear in two columns
g_col1, g_col2 = st.columns(2)
half = len(gear) // 2
with g_col1:
    for item in gear[:half]:
        st.success(item)
with g_col2:
    for item in gear[half:]:
        st.success(item)

# Weather Plot

st.divider()
st.subheader("📅 Temperature & Wind Outlook")

times = [p["Time of Day"] for p in forecast]

fig = go.Figure()

# Temperature as line
fig.add_trace(
    go.Scatter(
        x=times,
        y=temps,
        mode="lines+markers",
        name="Temp (F)",
        line=dict(color="firebrick", width=2),
    )
)

# Wind as bar
fig.add_trace(
    go.Bar(
        x=times,
        y=winds,
        name="Wind (mph)",
        marker_color="royalblue",
        opacity=0.6,
        yaxis="y2",
    )
)

# Dual axis layout
fig.update_layout(
    title=f"Weather Forecast for {selected_park}",
    xaxis_title="Time of Day",
    yaxis=dict(title="Temperature (°F)", side="left"),
    yaxis2=dict(title="Wind (mph)", overlaying="y", side="right"),
    legend=dict(x=0.01, y=0.99),
)

st.plotly_chart(fig, use_container_width=True)


st.markdown("Weather Data From: [weather.gov](https://www.weather.gov/).")
