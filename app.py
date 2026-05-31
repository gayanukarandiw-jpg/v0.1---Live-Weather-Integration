import streamlit as st 
import pandas as pd
import requests

st.title("Sri Lankan Flood Risk Predictor")
st.subheader("Select Your District")

df= pd.read_csv("data/districts.csv")
selected_district = st.selectbox("Districts: ", df["District"])
district_info = df[df["District"] == selected_district].iloc[0]
lat = district_info["Latitude"]
long = district_info["Longitude"]
elevation = district_info["Elevation"]

st.write("Selected District is :", selected_district)

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
        

if st.button("Analyze"):
    weather = get_live_weather(lat, long)  
    current = weather["current_weather"]
    rain_today = weather["daily"]["precipitation_sum"][0]
    date_today = weather["daily"]["time"][0]
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Rainfall Forecast",
            f"{rain_today} mm"
        )
        st.metric(
            "Temperature",
            f"{current['temperature']} °C"
        )
    with col2:
        st.metric(
            "Elevation",
            f"{elevation} m"
        )
        st.metric(
            "Wind Speed",
            f"{current['windspeed']} km/h"
        )
    if rain_today > 100 and elevation < 100:
        risk = "HIGH"
        st.error("🔴 HIGH FLOOD RISK")
    elif rain_today > 50:
        risk = "MEDIUM"
        st.warning("🟡 MEDIUM FLOOD RISK")
    else:
        risk = "LOW"
        st.success("🟢 LOW FLOOD RISK")
