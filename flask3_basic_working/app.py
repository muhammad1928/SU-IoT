from flask import Flask, render_template, jsonify  # Import necessary Flask modules
import threading  # Import threading for concurrent execution
import time  # Import time for sleep and time operations
import requests  # Import requests for HTTP requests
from datetime import datetime  # Import datetime for date and time operations
import RPi.GPIO as GPIO  # Import GPIO for Raspberry Pi GPIO operations
from threading import Lock  # Import Lock for thread-safe operations

app = Flask(__name__)  # Initialize Flask application

# Global variables and constants
lights = {
    "lightlevel0": "#cccccc",  # Light level for clear day
    "lightlevel1": "#fff394",  # Light level for cloudy day or night with motion
    "lightlevel2": "#ffd500",  # Light level for night with bad weather
}

PIR_PIN = 12  # GPIO pin for PIR sensor
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"  # Base URL for weather API
light = {"lightlevel": None}  # Dictionary to store current light level
gpio_lock = Lock()  # Add thread-safe lock for GPIO operations

# Read API key from file
try:
    with open("api.txt", "r") as f:  # Open API key file
        API_KEY = f.read().strip()  # Read and strip API key
except FileNotFoundError:
    raise ValueError("API Key file not found. Please create 'api.txt' and add the API key.")  # Raise error if file not found

class PIRController:
    def __init__(self, pin):
        self.pin = pin  # Initialize pin
        self.setup_complete = False  # Setup flag
        
    def setup(self):
        with gpio_lock:  # Ensure thread-safe GPIO setup
            if not self.setup_complete:  # Check if setup is not complete
                GPIO.setmode(GPIO.BCM)  # Set GPIO mode
                GPIO.setup(self.pin, GPIO.IN)  # Setup GPIO pin as input
                self.setup_complete = True  # Mark setup as complete
    
    def cleanup(self):
        with gpio_lock:  # Ensure thread-safe GPIO cleanup
            if self.setup_complete:  # Check if setup is complete
                GPIO.cleanup()  # Cleanup GPIO
                self.setup_complete = False  # Mark setup as not complete
    
    def read_motion(self):
        with gpio_lock:  # Ensure thread-safe GPIO read
            return GPIO.input(self.pin)  # Read GPIO pin input

def get_weather_data(city):
    global weather_description  # Use global variable for weather description
    """Fetch weather data and determine light level needed"""
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}  # Set parameters for API request
        response = requests.get(BASE_URL, params=params)  # Make API request
        response.raise_for_status()  # Raise error for bad response
        
        data = response.json()  # Parse JSON response
        main = data.get('main', {})  # Get main weather data
        weather = data.get('weather', [{}])[0]  # Get weather description
        sys = data.get('sys', {})  # Get system data
        
        dt = data.get('dt')  # Get current time
        sunrise = sys.get('sunrise')  # Get sunrise time
        sunset = sys.get('sunset')  # Get sunset time
        weather_description = weather.get('main')  # Get main weather description
        danger_zone = True  # You might want to implement logic for this
        
        # Determine light status based on conditions
        if not (sunrise <= dt <= sunset):  # Night time
            if not danger_zone:
                if weather_description == "Clear":
                    return "waitfor1", True  # Return light level and status
                elif weather_description in ["Rain", "Thunderstorm"]:
                    return "waitfor2", False  # Return light level and status
                else:  # Cloudy, Snow, or Mist
                    return "waitfor1", True  # Return light level and status
            else:  # Danger zone
                if weather_description in ["Thunderstorm", "Rain", "Mist", "Snow"]:
                    return "lightis2", False  # Return light level and status
                else:
                    return "waitfor2", False  # Return light level and status
        else:  # Day time
            if weather_description == "Clear":
                return "lightis0", True  # Return light level and status
            elif weather_description in ["Thunderstorm", "Snow"]:
                return "lightis2", False  # Return light level and status
            else:
                return "waitfor2", True  # Return light level and status
                
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")  # Print error message
        return "waitfor1", True  # Default safe mode

def pir_monitoring_loop(pir_controller):
    """Main monitoring loop with proper resource management"""
    try:
        while True:
            weather_status, lights_off = get_weather_data("Stockholm")  # Get weather data
            
            if weather_status == "lightis2":
                light["lightlevel"] = lights["lightlevel2"]  # Set light level
                time.sleep(5)  # Check weather every 5 seconds
                
            elif weather_status == "lightis0":
                light["lightlevel"] = lights["lightlevel0"]  # Set light level
                time.sleep(5)  # Check weather every 5 seconds
                
            elif weather_status == "waitfor1":
                check_motion_with_timeout(pir_controller, 
                                       base_level=lights["lightlevel0"],
                                       motion_level=lights["lightlevel1"],
                                       timeout=600)  # Check motion with timeout
                
            else:  # waitfor2
                check_motion_with_timeout(pir_controller,
                                       base_level=lights["lightlevel1"],
                                       motion_level=lights["lightlevel2"],
                                       timeout=600)  # Check motion with timeout
                
    except Exception as e:
        print(f"Error in monitoring loop: {e}")  # Print error message
    finally:
        pir_controller.cleanup()  # Cleanup PIR controller

def check_motion_with_timeout(pir_controller, base_level, motion_level, timeout):
    """Check motion for a specified time period"""
    start_time = time.time()  # Get start time
    light["lightlevel"] = base_level  # Set base light level
    
    while time.time() - start_time < timeout:  # Loop until timeout
        for _ in range(5):  # Check motion 5 times
            if pir_controller.read_motion():  # Read motion
                light["lightlevel"] = motion_level  # Set motion light level
                print("Motion detected!")  # Print motion detected
            else:
                light["lightlevel"] = base_level  # Set base light level
                print("No motion detected")  # Print no motion detected
            time.sleep(1)  # Sleep for 1 second

def start_monitoring():
    """Initialize and start the monitoring thread"""
    pir_controller = PIRController(PIR_PIN)  # Initialize PIR controller
    try:
        pir_controller.setup()  # Setup PIR controller
        monitoring_thread = threading.Thread(
            target=pir_monitoring_loop,
            args=(pir_controller,),
            daemon=True
        )  # Create monitoring thread
        monitoring_thread.start()  # Start monitoring thread
    except Exception as e:
        print(f"Error starting monitoring: {e}")  # Print error message
        pir_controller.cleanup()  # Cleanup PIR controller

@app.route("/light-status")
def light_status():
    return jsonify(light, weather_description)  # Return light status as JSON

@app.route("/")
def index():
    return render_template("index.html")  # Render index.html template

if __name__ == '__main__':
    start_monitoring()  # Start monitoring
    app.run(host='0.0.0.0', port=8080, debug=False)  # Run Flask app on port 8080 with debug mode off