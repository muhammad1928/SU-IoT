import os
import requests
from flask import Flask, render_template

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

# Weather condition to background mapping
WEATHER_BACKGROUND_MAP = {
    "Clear": "#cccccc",  # Light off (grey) for clear sky
    "Clouds": "#fffe38",  # Level 1 light on (light yellow) for cloudy
    "Rain": "#fffe38",  # Level 1 light on (light yellow) for rain
    "Snow": "#cccccc",  # Light off (grey) for snow
    "Thunderstorm": "#ffd13b",  # Level 2 light on (yellow) for thunderstorm
    "Mist": "#fffe38",  # Level 1 light on (light yellow) for mist
    "Default": "#cccccc",  # Default background color
    "sunrise": "#cccccc",
    "sunset": "#fffe38"
}

def get_weather_data(city):
    """Fetch weather data and determine background color, description, and reasoning."""
    params = {"q": city, "appid": API_KEY, "units": "metric"}  # Metric units for Celsius
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        weather_data = response.json()
        condition = weather_data["weather"][0]["main"]
        description = weather_data["weather"][0]["description"].capitalize()
        temp = weather_data["main"]["temp"]
        sys_info = weather_data["sys"]
        current_time = weather_data["dt"]
        sunrise = sys_info["sunrise"]
        sunset = sys_info["sunset"]

        # Check for sunrise or sunset
        if current_time <= sunrise + 3600:  # Within 1 hour of sunrise
            background_color = WEATHER_BACKGROUND_MAP.get("sunrise", WEATHER_BACKGROUND_MAP["Default"])
            reason = "It's around sunrise, so the color is dark."
        elif current_time >= sunset - 3600:  # Within 1 hour of sunset
            background_color = WEATHER_BACKGROUND_MAP.get("sunset", WEATHER_BACKGROUND_MAP["Default"])
            reason = "It's around sunset, so the color is light."
        else:
            background_color = WEATHER_BACKGROUND_MAP.get(condition, WEATHER_BACKGROUND_MAP["Default"])
            reason = f"The background color is based on the current weather condition: {condition.lower()}."

        return {
            "background_color": background_color,
            "description": f"{description}, {temp}°C",
            "reason": reason
        }


@app.route("/")
def index():
    city = "Stockholm"  # Stockholm, Sweden by default
    weather_data = get_weather_data(city)
    return render_template(
        "index.html",
        background_color=weather_data["background_color"],
        weather_description=weather_data["description"],
        color_reason=weather_data["reason"]
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=True)
