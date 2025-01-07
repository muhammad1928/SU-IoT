import os
import requests
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# Read API key from api-weather.txt
try:
    f = open("../../api-weather.txt", "r")
    API_KEY = f.read().strip()
    f.close()
except FileNotFoundError:
    raise ValueError("API Key file not found. Please create 'api-weather.txt' and add the API key.")

# OpenWeatherMap base URL
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Weather condition to background color mapping
WEATHER_BACKGROUND_MAP = {
    "Clear": "#cccccc",  # Light off (grey) for clear sky
    "Clouds": "#fffe38",  # Level 1 light on (light yellow) for cloudy
    "Rain": "#fffe38",  # Level 1 light on (light yellow) for rain
    "Snow": "#cccccc",  # Light off (grey) for snow
    "Thunderstorm": "#ffd13b",  # Level 2 light on (yellow) for thunderstorm
    "Mist": "#fffe38",  # Level 1 light on (light yellow) for mist
    "Default": "#cccccc"  # Default background color
}

# Default light status
CURRENT_LIGHT_COLOR = "#cccccc"
MOTION_DETECTED_COUNT = 0  # Default motion count

def get_weather_data(city):
    """Fetch weather data and determine background color and description."""
    params = {"q": city, "appid": API_KEY, "units": "metric"}  # Metric units for Celsius
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        weather_data = response.json()
        condition = weather_data["weather"][0]["main"]
        description = weather_data["weather"][0]["description"].capitalize()
        temp = weather_data["main"]["temp"]

        # Use weather condition for background color
        background_color = WEATHER_BACKGROUND_MAP.get(condition, WEATHER_BACKGROUND_MAP["Default"])

        return {
            "description": f"{description}, {temp}°C",
            "background_color": background_color
        }
    return {
        "description": "Unable to fetch weather data",
        "background_color": WEATHER_BACKGROUND_MAP["Default"]
    }

@app.route("/", methods=["GET", "POST"])
def index():
    global CURRENT_LIGHT_COLOR, MOTION_DETECTED_COUNT

    # Get the current date and time
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Fetch weather data
    city = "Stockholm"  # Default city
    weather_data = get_weather_data(city)

    # Handle light controller button
    if request.method == "POST":
        current_color = request.form.get("current_light")
        if current_color == "#cccccc":
            CURRENT_LIGHT_COLOR = "#fffe38"
        elif current_color == "#fffe38":
            CURRENT_LIGHT_COLOR = "#ffd13b"
        elif current_color == "#ffd13b":
            CURRENT_LIGHT_COLOR = "#cccccc"

    # Simulate motion detected count for now
    MOTION_DETECTED_COUNT += 1  # Increment on every page load (for demonstration)

    return render_template(
        "index.html",
        date_time=date_time,
        weather_description=weather_data["description"],
        background_color=weather_data["background_color"],
        light_color=CURRENT_LIGHT_COLOR,
        motion_count=MOTION_DETECTED_COUNT
    )

if __name__ == "__main__":
    app.run(debug=True)