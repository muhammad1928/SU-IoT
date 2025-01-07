from flask import Flask, render_template
import RPi.GPIO as GPIO
import requests
from datetime import datetime
import time
import threading

app = Flask(__name__)

# Read API key from api-weather.txt
try:
    f = open("../../api-weather.txt", "r")
    API_KEY = f.read().strip()
    f.close()
except FileNotFoundError:
    raise ValueError("API Key file not found. Please create 'api-weather.txt' and add the API key.")

LOCATION ="Stockholm"
# OpenWeatherMap base URL
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# PIR Sensor Configuration
PIR_PIN = 12  # GPIO pin connected to the PIR sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# Light colors
LIGHT_OFF = "#000000"  # No light
LIGHT_LOW = "#ffe385"  # Little light
LIGHT_HIGH = "#ffd13b"  # Full light


def monitor_motion():
    """
    Monitors the PIR sensor and updates the global motion_detected variable.
    Runs in a separate thread to ensure Flask remains responsive.
    """
    global motion_detected
    while True:
        motion_detected = GPIO.input(PIR_PIN)
        time.sleep(1)  # Polling interval

@app.route("/")
def index():
    # Fetch weather data from OpenWeatherMap API
    params = {
        "q": LOCATION,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(BASE_URL, params=params)
    weather_data = response.json()

    # Extract necessary details
    temperature = weather_data["main"]["temp"]
    description = weather_data["weather"][0]["description"]
    sunrise = datetime.fromtimestamp(weather_data["sys"]["sunrise"])
    sunset = datetime.fromtimestamp(weather_data["sys"]["sunset"])
    current_time = datetime.now()

    # Determine if it is day or night
    is_daytime = sunrise <= current_time <= sunset

    # Use the global motion state
    global motion_detected

    return render_template(
        "index.html",
        location=LOCATION,
        temperature=temperature,
        description=description,
        is_daytime=is_daytime,
        is_motion_detected=motion_detected
    )

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=True,)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        GPIO.cleanup()