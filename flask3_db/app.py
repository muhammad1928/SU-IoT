from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import time
from datetime import datetime
import RPi.GPIO as GPIO
from threading import Lock
import sqlite3
import requests
import os

app = Flask(__name__)
CORS(app)

# Global variables
lights = {
    "lightlevel0": "#cccccc",  # Default/Off
    "lightlevel1": "#fff394",  # Medium
    "lightlevel2": "#ffd500"   # Bright
}

# GPIO Setup
PIR_PIN = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

light = {"lightlevel": lights["lightlevel0"]}
gpio_lock = Lock()

# OpenWeatherMap configuration
OPENWEATHER_API_KEY = "0e9dd472bbe5550f46dede87c043e482"
CITY_ID = "2673730"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_db_connection():
    try:
        conn = sqlite3.connect('sensor_data.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Could not connect to database")
            
        c = conn.cursor()
        
        # Create motion_events table
        c.execute('''CREATE TABLE IF NOT EXISTS motion_events
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      weather_condition TEXT,
                      temperature REAL,
                      humidity REAL,
                      wind_speed REAL,
                      is_day BOOLEAN,
                      light_level TEXT)''')
        
        # Create weather_log table
        c.execute('''CREATE TABLE IF NOT EXISTS weather_log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      weather_condition TEXT,
                      weather_description TEXT,
                      temperature REAL,
                      humidity REAL,
                      wind_speed REAL,
                      is_day BOOLEAN)''')
        
        conn.commit()
        print("Database tables created successfully")
        conn.close()
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

def get_weather_data():
    """Fetch real weather data from OpenWeatherMap API"""
    try:
        params = {
            'id': CITY_ID,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(BASE_URL, params=params)
        if response.status_code != 200:
            print(f"Weather API error: {response.status_code}")
            return None
            
        data = response.json()
        
        return {
            'weather': data['weather'][0]['main'],
            'temperature': data['main']['temp'],
            'is_day': 6 <= datetime.now().hour < 18,  # Simple day/night check
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed']
        }
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def log_weather_change():
    """Log weather changes to database"""
    try:
        weather_data = get_weather_data()
        if weather_data:
            conn = get_db_connection()
            if not conn:
                return
                
            c = conn.cursor()
            c.execute('''INSERT INTO weather_log 
                         (weather_condition, weather_description, temperature, 
                          humidity, wind_speed, is_day)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (weather_data['weather'],
                       weather_data['description'],
                       weather_data['temperature'],
                       weather_data['humidity'],
                       weather_data['wind_speed'],
                       weather_data['is_day']))
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Error logging weather: {e}")

def log_motion_event(weather_data):
    """Log motion detection with weather data"""
    try:
        conn = get_db_connection()
        if not conn:
            return
            
        c = conn.cursor()
        c.execute('''INSERT INTO motion_events 
                     (weather_condition, temperature, humidity,
                      wind_speed, is_day, light_level)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (weather_data['weather'],
                   weather_data['temperature'],
                   weather_data['humidity'],
                   weather_data['wind_speed'],
                   weather_data['is_day'],
                   light["lightlevel"]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging motion: {e}")

def motion_detected():
    """Handle motion detection"""
    with gpio_lock:
        weather_data = get_weather_data()
        if weather_data:
            # Update light based on conditions
            if not weather_data['is_day']:
                light["lightlevel"] = lights["lightlevel2"]
            elif weather_data['weather'] in ["Rain", "Thunderstorm", "Snow"]:
                light["lightlevel"] = lights["lightlevel1"]
            else:
                light["lightlevel"] = lights["lightlevel0"]
            
            # Log motion event
            log_motion_event(weather_data)

def pir_sensor_thread():
    """Thread to monitor PIR sensor"""
    print("Starting PIR sensor monitoring")
    while True:
        try:
            if GPIO.input(PIR_PIN):
                motion_detected()
            time.sleep(0.1)
        except Exception as e:
            print(f"Error in PIR sensor thread: {e}")
            time.sleep(1)

def weather_update_thread():
    """Thread to update weather data"""
    print("Starting weather monitoring")
    while True:
        try:
            log_weather_change()
            time.sleep(300)
        except Exception as e:
            print(f"Error in weather thread: {e}")
            time.sleep(60)

# Flask routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/current-weather")
def current_weather():
    weather_data = get_weather_data()
    print("Weather Data:", weather_data)
    return jsonify(weather_data if weather_data else {"error": "Failed to fetch weather data"})

@app.route("/light-status")
def light_status():
    print("Light Status:", light)
    return jsonify(light)

@app.route("/get-statistics")
def get_stats():
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Database connection failed")

        c = conn.cursor()
        
        # Basic motion stats
        c.execute('SELECT COUNT(*) FROM motion_events')
        total_motions = c.fetchone()[0]
        
        # Weather condition counts
        c.execute('''SELECT weather_condition, COUNT(*) 
                     FROM motion_events 
                     GROUP BY weather_condition''')
        weather_counts = dict(c.fetchall()) or {}
        
        # Hourly distribution with default values
        hourly_dist = {str(i).zfill(2): 0 for i in range(24)}
        c.execute('''SELECT strftime('%H', timestamp) as hour, COUNT(*) 
                     FROM motion_events 
                     GROUP BY hour''')
        hourly_results = dict(c.fetchall())
        hourly_dist.update(hourly_results)
        
        stats = {
            "total_motions": total_motions,
            "weather_counts": weather_counts,
            "hourly_distribution": hourly_dist
        }
        
        conn.close()
        print("Returning stats:", stats)
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error in get_statistics: {e}")
        return jsonify({
            "error": str(e),
            "total_motions": 0,
            "weather_counts": {},
            "hourly_distribution": {str(i).zfill(2): 0 for i in range(24)}
        })

@app.route("/mock-motion", methods=["POST"])
def mock_motion():
    """Endpoint for mock motion trigger"""
    try:
        motion_detected()
        return jsonify({"message": "Motion detected", "light_level": light["lightlevel"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.before_request
def init_app():
    if not app.initialized:
        try:
            init_db()  # Replace with your actual database initialization function
            app.initialized = True
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")

if __name__ == '__main__':
    try:
        print("Starting server initialization...")
        
        # Initialize database
        init_db()
        print("Database initialized")
        
        # Start background threads
        sensor_thread = threading.Thread(target=pir_sensor_thread, daemon=True)
        weather_thread = threading.Thread(target=weather_update_thread, daemon=True)
        
        print("Starting background threads...")
        sensor_thread.start()
        weather_thread.start()
        print("Background threads started")
        
        # Check database file
        if os.path.exists('sensor_data.db'):
            print("Database file exists")
            print(f"Database permissions: {oct(os.stat('sensor_data.db').st_mode)[-3:]}")
        else:
            print("Database file does not exist!")
        
        # Run Flask app
        print("Starting Flask server on port 8080...")
        app.run(host='0.0.0.0', port=8080, debug=True)
    except Exception as e:
        print(f"Error starting server: {e}")
    finally:
        GPIO.cleanup()