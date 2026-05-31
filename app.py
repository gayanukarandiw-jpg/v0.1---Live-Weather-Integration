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

st.write("Selected District is :", selected_district)

def get_live_weather(lat, long):   
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={long}"
        f"&current_weather=true"
        f"&daily=precipitation_sum"
    )
    response = requests.get(url)
    return response.json()

if st.button("Analyze"):
    weather = get_live_weather(lat, long)  
    # Current weather
    current = weather["current_weather"]
    st.write(f"Temperature: {current['temperature']} °C")
    st.write(f"Wind Speed: {current['windspeed']} km/h")
    # Daily rainfall
    rain_today = weather["daily"]["precipitation_sum"][0]
    date_today = weather["daily"]["time"][0]
    st.metric(
    "Today's Rainfall Forecast",
    f"{rain_today} mm"
)