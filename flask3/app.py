from flask import Flask, render_template, jsonify, request
import RPi.GPIO as GPIO
import time
import threading

# Set up GPIO
PIR_PIN = 12  # Change this to the GPIO pin you're using
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# Flask app setup
app = Flask(__name__)

motion_status = {"motion": False}
background_color = "#cccccc"
color_reason = "No motion detected."

# Function to monitor the PIR sensor in a separate thread
def monitor_motion():
    global motion_status
    try:
        print("PIR Sensor Ready...")
        while True:
            if GPIO.input(PIR_PIN):
                motion_status["motion"] = True
            else:
                motion_status["motion"] = False
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()

# Flask route to fetch motion status
@app.route("/motion_status", methods=["GET"])
def get_motion_status():
    return jsonify(motion_status)

# Flask route to render the HTML page
@app.route("/")
def home():
    return render_template(
        "index.html",
        background_color=background_color,
        weather_description="No motion detected.",
        color_reason=color_reason,
    )

# Flask route to update background dynamically via button presses
@app.route("/set_background", methods=["POST"])
def set_background():
    global background_color, color_reason
    data = request.json
    background_color = data.get("color", "#cccccc")
    color_reason = data.get("reason", "No motion detected.")
    return jsonify({"status": "success"})

if __name__ == "__main__":
    # Start the motion monitoring thread
    monitoring_thread = threading.Thread(target=monitor_motion, daemon=True)
    monitoring_thread.start()

    # Run the Flask app
    app.run(host="0.0.0.0", port=5000)
