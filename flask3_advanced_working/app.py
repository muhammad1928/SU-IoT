from flask import Flask, render_template, jsonify, request
import threading
import time
from datetime import datetime
import RPi.GPIO as GPIO
from threading import Lock

app = Flask(__name__)

# Global variables
lights = {
    "lightlevel0": "#cccccc",
    "lightlevel1": "#fff394",
    "lightlevel2": "#ffd500",
}

PIR_PIN = 12
light = {"lightlevel": lights["lightlevel0"]}
gpio_lock = Lock()

# Test scenario configurations
current_scenario = {
    "weather": "Clear",
    "is_day": True,
    "is_danger_zone": False
}

class MockWeatherResponse:
    def __init__(self, weather, is_day, is_danger_zone):
        self.weather = weather
        self.is_day = is_day
        self.is_danger_zone = is_danger_zone

    def get_status(self):
        if not self.is_day:  # Night time
            if not self.is_danger_zone:
                if self.weather == "Clear":
                    return "waitfor1", True
                elif self.weather in ["Rain", "Thunderstorm"]:
                    return "waitfor2", False
                else:  # Cloudy, Snow, or Mist
                    return "waitfor1", True
            else:  # Danger zone
                if self.weather in ["Thunderstorm", "Rain", "Mist", "Snow"]:
                    return "lightis2", False
                else:
                    return "waitfor2", False
        else:  # Day time
            if self.weather == "Clear":
                return "lightis0", True
            elif self.weather in ["Thunderstorm", "Snow"]:
                return "lightis2", False
            else:
                return "waitfor2", True

SCENARIO_CONFIGS = {
    "day_clear": {"weather": "Clear", "is_day": True, "is_danger_zone": False},
    "day_rain": {"weather": "Rain", "is_day": True, "is_danger_zone": False},
    "day_thunder": {"weather": "Thunderstorm", "is_day": True, "is_danger_zone": False},
    "day_cloudy": {"weather": "Clouds", "is_day": True, "is_danger_zone": False},
    "night_clear": {"weather": "Clear", "is_day": False, "is_danger_zone": False},
    "night_rain": {"weather": "Rain", "is_day": False, "is_danger_zone": False},
    "night_thunder": {"weather": "Thunderstorm", "is_day": False, "is_danger_zone": False},
    "night_cloudy": {"weather": "Clouds", "is_day": False, "is_danger_zone": False}
}

def get_weather_status():
    """Get weather status based on current test scenario"""
    mock_weather = MockWeatherResponse(
        current_scenario["weather"],
        current_scenario["is_day"],
        current_scenario["is_danger_zone"]
    )
    return mock_weather.get_status()

def update_light_status():
    """Update light status based on current weather and motion"""
    weather_status, _ = get_weather_status()
    
    if weather_status == "lightis2":
        light["lightlevel"] = lights["lightlevel2"]
    elif weather_status == "lightis0":
        light["lightlevel"] = lights["lightlevel0"]
    elif weather_status == "waitfor1":
        # Default to level 0, motion will trigger level 1
        light["lightlevel"] = lights["lightlevel0"]
    else:  # waitfor2
        # Default to level 1, motion will trigger level 2
        light["lightlevel"] = lights["lightlevel1"]

@app.route("/set-scenario", methods=["POST"])
def set_scenario():
    scenario = request.json.get("scenario")
    if scenario in SCENARIO_CONFIGS:
        global current_scenario
        current_scenario = SCENARIO_CONFIGS[scenario]
        update_light_status()
        return jsonify({
            "message": f"Scenario set to {scenario}",
            "weather": current_scenario["weather"],
            "is_day": current_scenario["is_day"]
        })
    return jsonify({"error": "Invalid scenario"}), 400

@app.route("/trigger-motion", methods=["POST"])
def trigger_motion():
    weather_status, _ = get_weather_status()
    
    if weather_status == "waitfor1":
        light["lightlevel"] = lights["lightlevel1"]
        message = "Motion detected - Light set to level 1"
    elif weather_status == "waitfor2":
        light["lightlevel"] = lights["lightlevel2"]
        message = "Motion detected - Light set to level 2"
    else:
        message = "Motion detected - No change in light level"
    
    return jsonify({"message": message})

@app.route("/light-status")
def light_status():
    return jsonify(light)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)