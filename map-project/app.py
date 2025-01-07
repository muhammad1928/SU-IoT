from flask import Flask, render_template, jsonify
import threading
import time
import random  # Used to simulate motion on Windows

app = Flask(__name__)

# Simulated motion state (mock for PIR sensor)
motion_detected = False

def monitor_motion():
    """
    Simulates a PIR sensor by randomly setting motion_detected.
    Runs in a separate thread to ensure Flask remains responsive.
    """
    global motion_detected
    while True:
        # Randomly toggle motion_detected to simulate motion
        motion_detected = random.choice([True, False])
        time.sleep(1)  # Polling interval (simulated sensor delay)

# Start the motion simulation in a separate thread
motion_thread = threading.Thread(target=monitor_motion, daemon=True)
motion_thread.start()

@app.route("/")
def index():
    """
    Render the main webpage with the map.
    """
    return render_template("index.html")

@app.route("/motion")
def get_motion_data():
    """
    Returns the current motion sensor state as JSON.
    """
    global motion_detected
    return jsonify({"motion_detected": motion_detected})

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("Shutting down...")
