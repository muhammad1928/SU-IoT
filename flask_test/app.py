from flask import Flask, render_template
from gpiozero import MotionSensor
from threading import Thread
import time

app = Flask(__name__)

# Define the GPIO pin number for the PIR sensor
pir = MotionSensor(12)

# Global variable to store the current background color
background_color = "black"  # Start with a dark color

def monitor_motion():
    """Thread function to monitor motion and update the background color."""
    global background_color
    while True:
        if pir.motion_detected:
            print("Motion detected! Switching to light color.")
            background_color = "white"  # Light color when motion is detected
        else:
            print("No motion detected. Switching to dark color.")
            background_color = "black"  # Dark color when no motion is detected
        time.sleep(0.1)  # Small delay to reduce rapid updates

@app.route("/")
def index():
    """Serve the webpage with the current background color."""
    global background_color
    return render_template("index.html", color=background_color)

if __name__ == "__main__":
    # Start the motion detection thread
    motion_thread = Thread(target=monitor_motion, daemon=True)
    motion_thread.start()

    # Run the Flask app
    app.run(debug=True, host="0.0.0.0")  # Set to 0.0.0.0 to make it accessible on the network
