from flask import Flask, render_template, jsonify
import threading
import time
import requests
from datetime import datetime
import RPi.GPIO as GPIO
from threading import Lock

app = Flask(__name__)

# Global variables and constants
lights = {
    "lightlevel0": "#cccccc",
    "lightlevel1": "#fff394",
    "lightlevel2": "#ffd500",
}

PIR_PIN = 12
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
light = {"lightlevel": None}
gpio_lock = Lock()  # Add thread-safe lock for GPIO operations

# Read API key
try:
    with open("api.txt", "r") as f:
        API_KEY = f.read().strip()
except FileNotFoundError:
    raise ValueError("API Key file not found. Please create 'api.txt' and add the API key.")

class PIRController:
    def __init__(self, pin):
        self.pin = pin
        self.setup_complete = False
        
    def setup(self):
        with gpio_lock:
            if not self.setup_complete:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.pin, GPIO.IN)
                self.setup_complete = True
    
    def cleanup(self):
        with gpio_lock:
            if self.setup_complete:
                GPIO.cleanup()
                self.setup_complete = False
    
    def read_motion(self):
        with gpio_lock:
            return GPIO.input(self.pin)

def get_weather_data(city):
    """Fetch weather data and determine light level needed"""
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        sys = data.get('sys', {})
        
        dt = data.get('dt')
        sunrise = sys.get('sunrise')
        sunset = sys.get('sunset')
        weather_description = weather.get('main')
        danger_zone = True  # You might want to implement logic for this
        
        # Determine light status based on conditions
        if not (sunrise <= dt <= sunset):  # Night time
            if not danger_zone:
                if weather_description == "Clear":
                    return "waitfor1", True
                elif weather_description in ["Rain", "Thunderstorm"]:
                    return "waitfor2", False
                else:  # Cloudy, Snow, or Mist
                    return "waitfor1", True
            else:  # Danger zone
                if weather_description in ["Thunderstorm", "Rain", "Mist", "Snow"]:
                    return "lightis2", False
                else:
                    return "waitfor2", False
        else:  # Day time
            if weather_description == "Clear":
                return "lightis0", True
            elif weather_description in ["Thunderstorm", "Snow"]:
                return "lightis2", False
            else:
                return "waitfor2", True
                
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return "waitfor1", True  # Default safe mode

def pir_monitoring_loop(pir_controller):
    """Main monitoring loop with proper resource management"""
    try:
        while True:
            weather_status, lights_off = get_weather_data("Stockholm")
            
            if weather_status == "lightis2":
                light["lightlevel"] = lights["lightlevel2"]
                time.sleep(5)  # Check weather every 5 seconds
                
            elif weather_status == "lightis0":
                light["lightlevel"] = lights["lightlevel0"]
                time.sleep(5)
                
            elif weather_status == "waitfor1":
                check_motion_with_timeout(pir_controller, 
                                       base_level=lights["lightlevel0"],
                                       motion_level=lights["lightlevel1"],
                                       timeout=600)
                
            else:  # waitfor2
                check_motion_with_timeout(pir_controller,
                                       base_level=lights["lightlevel1"],
                                       motion_level=lights["lightlevel2"],
                                       timeout=600)
                
    except Exception as e:
        print(f"Error in monitoring loop: {e}")
    finally:
        pir_controller.cleanup()

def check_motion_with_timeout(pir_controller, base_level, motion_level, timeout):
    """Check motion for a specified time period"""
    start_time = time.time()
    light["lightlevel"] = base_level
    
    while time.time() - start_time < timeout:
        for _ in range(5):  # Check motion 5 times
            if pir_controller.read_motion():
                light["lightlevel"] = motion_level
                print("Motion detected!")
            else:
                light["lightlevel"] = base_level
                print("No motion detected")
            time.sleep(1)

def start_monitoring():
    """Initialize and start the monitoring thread"""
    pir_controller = PIRController(PIR_PIN)
    try:
        pir_controller.setup()
        monitoring_thread = threading.Thread(
            target=pir_monitoring_loop,
            args=(pir_controller,),
            daemon=True
        )
        monitoring_thread.start()
    except Exception as e:
        print(f"Error starting monitoring: {e}")
        pir_controller.cleanup()

@app.route("/light-status")
def light_status():
    return jsonify(light)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    start_monitoring()
    app.run(host='0.0.0.0', port=8080, debug=False)  # Debug mode set to False for production