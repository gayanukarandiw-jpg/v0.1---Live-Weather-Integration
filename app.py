import streamlit as st 
import pandas as pd
import requests
from PIL import Image
import folium
from streamlit_folium import st_folium
import plotly.express as px
from streamlit_lottie import st_lottie
import time
import json

icon = Image.open("icons/wp_icon.png")
st.set_page_config(page_title="Flood Risk Predictor", page_icon=icon, layout="wide")
with open("assets/Rainy.json", "r") as anime:
    rain_anime = json.load(anime)
col1, col2 = st.columns([2, 43])
with col1:
    st.write("")
    st_lottie(rain_anime, height=50, width=50, key="rain_icon")
with col2:
    st.markdown("## Sri Lankan Flood Risk Predictor")
df= pd.read_csv("data/districts.csv")
tab1, tab2 = st.tabs(["📊 District Analysis", "🌍 Island-Wide Overview"])
st.caption("Data Source: Open-Meteo API | Built with Streamlit, Folium, and Plotly")
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_live_weather(lat, long):   
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={long}"
        f"&current_weather=true"
        f"&daily=precipitation_sum,temperature_2m_max"
    )
    try:       
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Weather API Error: {e}")
        return None
    
with tab1:
    st.subheader("🗺️ Select Your District")
    selected_district = st.selectbox("Districts: ", df["District"], index=None, placeholder="Choose a district")
    if selected_district is None:
        st.info("Please select a district.")
    else:
        district_info = df[df["District"] == selected_district].iloc[0]
        st.write("Selected District is :", selected_district) 
        district_info = df[df["District"] == selected_district].iloc[0]
        lat = district_info["Latitude"]
        long = district_info["Longitude"]
        elevation = district_info["Elevation"]
        weather = get_live_weather(lat, long)
        if selected_district is None:
            st.info("Please select a district.")
        else:
        # District Analysis code
            current = weather["current_weather"]
            rain_today = weather["daily"]["precipitation_sum"][0]
            date_today = weather["daily"]["time"][0]
            forecast_df = pd.DataFrame({"Date": weather["daily"]["time"], "Rainfall": weather["daily"]["precipitation_sum"]})
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🌧️ Rainfall Forecast", f"{rain_today} mm")
                st.metric("🌡️ Temperature", f"{current['temperature']} °C")
            with col2:
                st.metric("⛰️ Elevation", f"{elevation} m")
                st.metric("🍃 Wind Speed", f"{current['windspeed']} km/h")
                    
            if rain_today > 100 and elevation < 100:
                risk = "HIGH"
                st.error("🔴 HIGH FLOOD RISK")
            elif rain_today > 50:
                risk = "MEDIUM"
                st.warning("🟡 MEDIUM FLOOD RISK")
            else:
                risk = "LOW"
                st.success("🟢 LOW FLOOD RISK")
            
            fig = px.bar(forecast_df, x="Date", y="Rainfall", title=f"Rainfall Forecast for {selected_district}")
            m = folium.Map(location=[lat, long], zoom_start=8)
            folium.CircleMarker(
                location=[lat, long],
                radius=20,
                popup=f"{selected_district}: {risk} Risk",
                color='red' if risk=='HIGH' else 'yellow' if risk=='MEDIUM' else 'green',
                fill=True,
                fill_color='red' if risk=='HIGH' else 'yellow' if risk=='MEDIUM' else 'green'
                ).add_to(m)
            col1, col2 = st.columns(2)
            fig = px.bar(forecast_df, x="Date", y="Rainfall", title=f"Rainfall Forecast for {selected_district}")
            with col1:
                st_folium(m, width=700)
            with col2:
                st.subheader("📈 7-Day Rainfall Forecast")
                st.plotly_chart(fig, use_container_width=True, key=f"forecast_chart_{selected_district}")
                fig.update_layout(height=500)
            st.caption(f"Forecast Date: {date_today}")
            st.markdown("---")

with tab2:   
    st.subheader("🌍 Sri Lanka Flood Risk Overview")
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=7)
    high_risk = 0
    medium_risk = 0
    low_risk = 0
    with st.spinner("Fetching live weather for all districts..."):
        for index, row in df.iterrows():
            district = row["District"]
            lat = row["Latitude"]
            lon = row["Longitude"]
            elevation = row["Elevation"]
            weather = get_live_weather(lat, lon)
            if weather is None:
                continue
            rain_today = weather["daily"]["precipitation_sum"][0]
            
            # Risk calculation
            if rain_today > 100 and elevation < 100:
                risk = "HIGH"
                color = "red"
                high_risk += 1
            elif rain_today > 50:
                risk = "MEDIUM"
                color = "yellow"
                medium_risk += 1
            else:
                risk = "LOW"
                color = "green"
                low_risk += 1

            radius = 15 
            popup = f"{district}: {risk} Risk"
            popup = (
                    f"{district}<br>"
                    f"Rainfall: {rain_today} mm<br>"
                    f"Elevation: {elevation} m<br>"
                    f"Risk: {risk}"
                    )
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=popup,
                color=color,
                fill=True,
                fill_color=color,
                tooltip=district # Hover to show the names
            ).add_to(m)

        # Display counters
        st.markdown(f"🔴 High Risk: {high_risk} | 🟡 Medium Risk: {medium_risk} | 🟢 Low Risk: {low_risk}")

        st_folium(m, width=700)