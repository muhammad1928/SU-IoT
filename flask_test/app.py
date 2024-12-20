import os
from flask import Flask, render_template, jsonify

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
    "Clear": "#000",  # Dark blue for clear sky
    "Clouds": "#00ffff",  # Light gray for cloudy
    "Rain": "#66ffff",  # Dark gray for rain
    "Snow": "#ffffcc",  # White for snow
    "Thunderstorm": "#ccffff",  # Dark slate for thunderstorm
    "Mist": "#ccffff",  # Light gray for mist
    "Sunrise": "#000",  # Warm orange for sunrise
    "Sunset": "#ccffff",  # Golden yellow for sunset
    "Default": "#87CEEB"  # Sky blue as default color
}

# Sample mock conditions
mock_conditions = [
    {"condition": "Clear", "description": "clear sky", "temp": 25, "color": "#000"},
    {"condition": "Clouds", "description": "overcast clouds", "temp": 18, "color": "#0ff"},
    {"condition": "Rain", "description": "light rain", "temp": 15, "color": "#6ff"},
    {"condition": "Snow", "description": "snow", "temp": -5, "color": "#ffc"},
    {"condition": "Thunderstorm", "description": "thunderstorm", "temp": 20, "color": "#cff"},
    {"condition": "Mist", "description": "misty", "temp": 12, "color": "#ccffff"},
    {"condition": "Sunrise", "description": "sunrise time", "temp": 10, "color": "#000"},
    {"condition": "Sunset", "description": "sunset time", "temp": 15, "color": "#cff"},
]

# Store the current index for cycling through conditions
condition_index = 0

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/weather_data")
def weather_data():
    global condition_index
    # Get the current weather condition
    current_condition = mock_conditions[condition_index]
    
    # Prepare the data to return
    weather_info = {
        "background_color": current_condition["color"],
        "description": f"{current_condition['description']}, {current_condition['temp']}°C",
        "reason": f"The background color is based on the condition: {current_condition['condition']}"
    }

    # Update the index for the next condition
    condition_index = (condition_index + 1) % len(mock_conditions)  # Cycle through conditions

    return jsonify(weather_info)

if __name__ == "__main__":
    app.run(debug=True,  port=8005)
