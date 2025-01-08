from flask import Flask, render_template, jsonify, request
import threading
import time
import RPi.GPIO as GPIO

app = Flask(__name__)

# GPIO setup
PIR_PIN = 12  # GPIO pin for PIR sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# Global light and motion status
light_status = {
    "light_level": "Off",
    "color": "#cccccc",
    "motion_detected": False,
    "manual_weather": None,  # For manual weather testing
    "previous_light_level": "Off",
    "previous_color": "#cccccc",
}

# Simulated weather conditions for testing
WEATHER_CONDITIONS = {
    "Clear": {"weather": "Clear", "color": "#cccccc", "level": "Off"},
    "Rain": {"weather": "Rain", "color": "#ffd500", "level": "Level 2"},
    "Thunderstorm": {"weather": "Thunderstorm", "color": "#ff6b6b", "level": "Level 2"},
    "Snow": {"weather": "Snow", "color": "#b3d9ff", "level": "Level 1"},
    "Cloudy": {"weather": "Cloudy", "color": "#fff394", "level": "Level 1"},
}

# Monitor PIR sensor in a background thread
def monitor_pir():
    while True:
        if GPIO.input(PIR_PIN):
            if not light_status["motion_detected"]:
                # Save the previous light level and color
                light_status["previous_light_level"] = light_status["light_level"]
                light_status["previous_color"] = light_status["color"]

                # Change the light level and color due to motion
                light_status["light_level"] = "Motion Detected"
                light_status["color"] = "#ffcccb"  # Red for motion detected

            light_status["motion_detected"] = True
        else:
            if light_status["motion_detected"]:
                # Revert back to the previous light level and color
                light_status["light_level"] = light_status["previous_light_level"]
                light_status["color"] = light_status["previous_color"]

            light_status["motion_detected"] = False

        time.sleep(1)

# Route for the homepage
@app.route("/")
def index():
    return render_template("index.html", light_status=light_status)

# Route to manually set weather conditions
@app.route("/set-weather", methods=["POST"])
def set_weather():
    condition = request.json.get("condition")
    if condition in WEATHER_CONDITIONS:
        light_status.update(WEATHER_CONDITIONS[condition])
    return jsonify(light_status)

# Route to fetch light status for dynamic updates
@app.route("/status")
def status():
    return jsonify(light_status)

if __name__ == "__main__":
    # Start PIR monitoring in a separate thread
    pir_thread = threading.Thread(target=monitor_pir)
    pir_thread.daemon = True
    pir_thread.start()
    app.run(host="0.0.0.0", port=5000)
