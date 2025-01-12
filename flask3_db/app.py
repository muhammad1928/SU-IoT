# app.py
from flask import Flask, jsonify, request
import sqlite3
import requests
from datetime import datetime
import RPi.GPIO as GPIO
import time
from threading import Thread

app = Flask(__name__)

# Configuration
OPENWEATHER_API_KEY = "YOUR_API_KEY"
CITY_NAME = "YOUR_CITY_NAME"  # e.g., "London" or "New York"
PIR_PIN = 17  # GPIO pin for PIR sensor
DATABASE = "motion_weather.db"
DANGER_ZONE_START = 22  # 10 PM
DANGER_ZONE_END = 5    # 5 AM

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS motion_events
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME,
                  weather_condition TEXT,
                  temperature FLOAT,
                  is_motion BOOLEAN)''')
    conn.commit()
    conn.close()

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return {
            'temperature': data['main']['temp'],
            'condition': data['weather'][0]['main'].lower(),
            'description': data['weather'][0]['description'],
            'success': True
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return {
            'temperature': 0,
            'condition': 'unknown',
            'description': 'Weather data unavailable',
            'success': False
        }

def is_danger_zone():
    current_hour = datetime.now().hour
    return DANGER_ZONE_START <= current_hour or current_hour < DANGER_ZONE_END

def is_daytime():
    current_hour = datetime.now().hour
    return 6 <= current_hour < 20

def determine_light_level(weather, has_motion):
    condition = weather['condition'].lower()
    
    if is_daytime():
        if condition == 'clear':
            return {'level': 0, 'color': '#cccccc'}
        elif condition in ['thunderstorm', 'snow']:
            return {'level': 2, 'color': '#ffd500'}
        else:  # mist, clouds, etc.
            return {'level': 2, 'color': '#ffd500'} if has_motion else {'level': 1, 'color': '#ffff394'}
    
    # Night time logic
    if is_danger_zone():
        if condition in ['thunderstorm', 'mist', 'snow', 'rain']:
            return {'level': 2, 'color': '#ffd500'}
        return {'level': 2, 'color': '#ffd500'} if has_motion else {'level': 1, 'color': '#ffff394'}
    
    # Regular night time
    if condition == 'clear':
        return {'level': 1, 'color': '#ffff394'} if has_motion else {'level': 0, 'color': '#cccccc'}
    elif condition in ['rain', 'thunderstorm', 'mist', 'snow', 'clouds']:
        return {'level': 2, 'color': '#ffd500'} if has_motion else {'level': 1, 'color': '#ffff394'}
    
    return {'level': 0, 'color': '#cccccc'}

def record_motion_event(weather, has_motion):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""INSERT INTO motion_events (timestamp, weather_condition, temperature, is_motion)
                 VALUES (?, ?, ?, ?)""",
              (datetime.now(), weather['condition'], weather['temperature'], has_motion))
    conn.commit()
    conn.close()

@app.route('/api/current-state')
def get_current_state():
    weather = get_weather()
    has_motion = GPIO.input(PIR_PIN) == GPIO.HIGH
    light_level = determine_light_level(weather, has_motion)
    
    # Get today's motion count
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM motion_events WHERE date(timestamp) = ? AND is_motion = 1", (today,))
    motion_count = c.fetchone()[0]
    conn.close()
    
    return jsonify({
        'temperature': weather['temperature'],
        'weather_condition': weather['condition'],
        'weather_description': weather['description'],
        'has_motion': has_motion,
        'light_level': light_level,
        'daily_motion_count': motion_count,
        'weather_success': weather['success']
    })

@app.route('/api/mock', methods=['POST'])
def mock_conditions():
    data = request.json
    # Handle mock data here
    return jsonify({'status': 'success', 'mock_data': data})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)