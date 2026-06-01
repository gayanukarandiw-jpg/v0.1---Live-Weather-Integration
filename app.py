import streamlit as st 
import pandas as pd
import requests
from PIL import Image
import folium
from streamlit_folium import st_folium

icon = Image.open("icons/wp_icon.png")
st.set_page_config(page_title="Flood Risk Predictor", page_icon=icon, layout="wide")
st.title("🌧️ Sri Lankan Flood Risk Predictor 🌧️")
df= pd.read_csv("data/districts.csv")
tab1, tab2 = st.tabs(["📊 District Analysis", "🌍 Island-Wide Overview"])
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_live_weather(lat, long):   
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={long}"
        f"&current_weather=true"
        f"&daily=precipitation_sum"
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
            m = folium.Map(location=[lat, long], zoom_start=8)
            folium.CircleMarker(
                location=[lat, long],
                radius=20,
                popup=f"{selected_district}: {risk} Risk",
                color='red' if risk=='HIGH' else 'yellow' if risk=='MEDIUM' else 'green',
                fill=True,
                fill_color='red' if risk=='HIGH' else 'yellow' if risk=='MEDIUM' else 'green'
                ).add_to(m)
            st_folium(m, width=700)
            st.caption(f"Forecast Date: {date_today}")
with tab2:   
    st.subheader("🌍 Sri Lanka Flood Risk Overview")
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=7)
    high_risk = 0
    medium_risk = 0
    low_risk = 0
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
            tooltip=district # Hover show names
        ).add_to(m)

    # Display counters
    st.markdown(f"🔴 High Risk: {high_risk} | 🟡 Medium Risk: {medium_risk} | 🟢 Low Risk: {low_risk}")

    st_folium(m, width=700)