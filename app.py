import os
from dotenv import load_dotenv
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from collections import Counter

load_dotenv()

st.set_page_config(
    page_title="Weather Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)
API_KEY = st.secrets["api_key"]
BASE_URL = "http://api.openweathermap.org/data/2.5"

# CSS Styling
st.markdown("""
    <style>
        /* General Styles */
        body {
            background-color: #f0f2f6;
        }
        h1, h2, h3, h4, h5, h6, p, div {
            text-align: center !important;
        }

        /* Title Styles */
        .title-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
        }
        .title-icon {
            font-size: 32px;
            margin-right: 10px;
        }

        /* Input Field */
        .stTextInput {
            max-width: 500px;
            margin: 0 auto;
        }

        /* Current Weather */
        .current-weather {
            background-color: #cfcfcf;
            border-radius: 10px;
            padding: 30px;
            margin: 20px auto;
            width: 50%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .weather-icon {
            width: 100px;
            height: 100px;
        }
        .temperature {
            font-size: 64px;
            font-weight: bold;
            margin: 20px 0;
            color: #333;
        }
        .weather-description {
            font-size: 24px;
            color: #555;
            text-transform: capitalize;
        }

        /* Metrics */
        .metric-container {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-icon {
            font-size: 32px;
            margin-bottom: 10px;
            color: #007BFF;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }
        .metric-label {
            font-size: 16px;
            color: #777;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 50px;
            color: #888;
        }
    </style>
""", unsafe_allow_html=True)

def get_current_weather(city_name):
    url = f"{BASE_URL}/weather"
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        weather = response.json()
        return {
            'temperature': weather['main']['temp'],
            'feels_like': weather['main']['feels_like'],
            'humidity': weather['main']['humidity'],
            'pressure': weather['main']['pressure'],
            'wind_speed': weather['wind']['speed'],
            'description': weather['weather'][0]['description'],
            'icon_url': f"http://openweathermap.org/img/wn/{weather['weather'][0]['icon']}@2x.png",
        }
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching weather data: {e}")
        return None

def get_forecast(city_name):
    url = f"{BASE_URL}/forecast"
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        forecast_data = response.json()
        forecast_list = []
        for item in forecast_data['list']:
            forecast_list.append({
                'datetime': datetime.fromtimestamp(item['dt']),
                'temperature': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'temp_min': item['main']['temp_min'],
                'temp_max': item['main']['temp_max'],
                'pressure': item['main']['pressure'],
                'humidity': item['main']['humidity'],
                'description': item['weather'][0]['description'],
            })
        return forecast_list
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching forecast data: {e}")
        return None

# Title Section
st.markdown("""
    <div class="title-container">
        <div class="title-icon">🌤️</div>
        <h1>Weather Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

# City Input
city_name = st.text_input("Enter City Name", "Ottawa")

if city_name:
    current_weather = get_current_weather(city_name)

    if current_weather:
        # Current Weather Display
        st.markdown(f"""
            <div class="current-weather">
                <img src="{current_weather['icon_url']}" class="weather-icon" alt="Weather Icon">
                <div class="temperature">{current_weather['temperature']}°C</div>
                <div class="weather-description">{current_weather['description']}</div>
            </div>
        """, unsafe_allow_html=True)

        # Weather Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-icon">🌡️</div>
                    <div class="metric-value">{current_weather['feels_like']}°C</div>
                    <div class="metric-label">Feels Like</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-icon">💧</div>
                    <div class="metric-value">{current_weather['humidity']}%</div>
                    <div class="metric-label">Humidity</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-icon">🌬️</div>
                    <div class="metric-value">{current_weather['wind_speed']} m/s</div>
                    <div class="metric-label">Wind Speed</div>
                </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-icon">🔽</div>
                    <div class="metric-value">{current_weather['pressure']} hPa</div>
                    <div class="metric-label">Pressure</div>
                </div>
            """, unsafe_allow_html=True)

        # Forecast Data
        forecast = get_forecast(city_name)
        if forecast:
            forecast_df = pd.DataFrame(forecast)

            # Temperature Forecast
            st.header("")
            st.subheader("📈 Temperature Forecast")
            temp_fig = go.Figure()
            temp_fig.add_trace(go.Scatter(
                x=forecast_df['datetime'],
                y=forecast_df['temperature'],
                name='Temperature',
                line=dict(color='firebrick', width=2),
                mode='lines+markers'
            ))
            temp_fig.add_trace(go.Scatter(
                x=forecast_df['datetime'],
                y=forecast_df['feels_like'],
                name='Feels Like',
                line=dict(color='royalblue', width=2, dash='dash'),
                mode='lines'
            ))
            temp_fig.update_layout(
                xaxis_title='Date & Time',
                yaxis_title='Temperature (°C)',
                legend=dict(y=1.1, orientation='h'),
                margin=dict(l=20, r=20, t=40, b=20),
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(gridcolor='rgba(200,200,200,0.3)'),
                yaxis=dict(gridcolor='rgba(200,200,200,0.3)')
            )
            st.plotly_chart(temp_fig, use_container_width=True)

            # Additional Charts
            st.markdown("---")
            col1, col2 = st.columns(2)

            # Weather Conditions Pie Chart
            with col1:
                st.subheader("📊 Weather Conditions")
                condition_counts = Counter(forecast_df['description'])
                condition_fig = go.Figure(data=[go.Pie(
                    labels=list(condition_counts.keys()),
                    values=list(condition_counts.values()),
                    hole=.4,
                    textinfo='percent+label'
                )])
                condition_fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(condition_fig, use_container_width=True)

            # Temperature Range
            with col2:
                st.subheader("🌡️ Temperature Range")
                range_fig = go.Figure()
                range_fig.add_trace(go.Scatter(
                    x=forecast_df['datetime'],
                    y=forecast_df['temp_max'],
                    name='Max Temp',
                    line=dict(color='red', width=2),
                    mode='lines'
                ))
                range_fig.add_trace(go.Scatter(
                    x=forecast_df['datetime'],
                    y=forecast_df['temp_min'],
                    name='Min Temp',
                    line=dict(color='blue', width=2),
                    mode='lines'
                ))
                range_fig.update_layout(
                    xaxis_title='Date & Time',
                    yaxis_title='Temperature (°C)',
                    legend=dict(y=1.1, orientation='h'),
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(gridcolor='rgba(200,200,200,0.3)'),
                    yaxis=dict(gridcolor='rgba(200,200,200,0.3)')
                )
                st.plotly_chart(range_fig, use_container_width=True)
        else:
            st.error("Unable to retrieve forecast data.")
    else:
        st.error("City not found. Please check the city name and try again.")

# Footer
st.markdown("---")
st.markdown("""
    <div class="footer">
        Weather data provided by OpenWeather API<br>
        A project by Kevin Chang
    </div>
""", unsafe_allow_html=True)
