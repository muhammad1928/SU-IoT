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

# Weather condition to background color mapping
WEATHER_BACKGROUND_MAP = {
    "Clear": "#cccccc",  # Light off (grey) for clear sky
    "Clouds": "#ffff394",  # Level 1 light on (light yellow) for cloudy
    "Rain": "#ffdc2e",  # Level 1 light on (light yellow) for rain
    "Snow": "#cccccc",  # Light off (grey) for snow
    "Thunderstorm": "#ffd13b",  # Level 2 light on (yellow) for thunderstorm
    "Mist": "#ffdc2e",  # Level 1 light on (light yellow) for mist
    "Default": "#cccccc"  # Default background color
}

# Color codes and their light statuses
LIGHT_STATUSES = {
    "#cccccc": "Light off",
    "#fffe38": "Light on min",
    "#ffd13b": "Light on max"
}

# Default light color
CURRENT_LIGHT_COLOR = None  # Start with None to use weather-based background by default

def get_weather_data(city):
    """Fetch weather data and determine background color and description."""
    params = {"q": city, "appid": API_KEY, "units": "metric"}  # Metric units for Celsius
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        weather_data = response.json()
        condition = weather_data["weather"][0]["main"]
        description = weather_data["weather"][0]["description"].capitalize()
        temp = weather_data["main"]["temp"]

        # Determine background color based on the weather condition
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
    global CURRENT_LIGHT_COLOR

    # Get the current date and time
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Fetch weather data
    city = "Stockholm"  # Default city
    weather_data = get_weather_data(city)

    # Determine the background color (weather-based or manually set)
    if request.method == "POST":
        action = request.form.get("action")
        if action == "off":
            CURRENT_LIGHT_COLOR = "#cccccc"
        elif action == "min":
            CURRENT_LIGHT_COLOR = "#fff394"
        elif action == "max":
            CURRENT_LIGHT_COLOR = "#ffdc2e"

    # Use manually set color or weather-based color
    background_color = CURRENT_LIGHT_COLOR if CURRENT_LIGHT_COLOR else weather_data["background_color"]

    # Determine the current light status
    current_light_status = LIGHT_STATUSES.get(background_color, "Unknown Status")

    # Simulate motion detected count for now
    motion_detected_count = 5  # Example static count

    return render_template(
        "index.html",
        date_time=date_time,
        weather_description=weather_data["description"],
        background_color=background_color,
        current_light_status=current_light_status,
        motion_count=motion_detected_count
    )

if __name__ == "__main__":
    app.run(debug=True)