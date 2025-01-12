from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime
import math
import requests
import RPi.GPIO as GPIO
import time
from threading import Thread

app = Flask(__name__)

# Global variables
light = "#cccccc"
PIR_PIN = 12
current_weather = "Unknown"

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# Read API key
try:
    with open("api.txt", "r") as f:
        API_KEY = f.read().strip()
except FileNotFoundError:
    raise ValueError("API Key file not found. Please create 'api.txt' and add the API key.")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# initialize database
def init_db():
    try:
        conn = sqlite3.connect('motion.db') # Create a database file called motion.db
        c = conn.cursor() # Create a cursor object
        # Create a table called motion_events with the following columns
        c.execute('''CREATE TABLE IF NOT EXISTS motion_events
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp TEXT,
                      date TEXT,
                      weather_condition TEXT)''')
        conn.commit() # Commit the changes
        conn.close() # Close the connection
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Log motion event to database
def log_motion_event(weather_condition):
    try:
        conn = sqlite3.connect('motion.db') # Connect to the database
        c = conn.cursor() # Create a cursor object
        now = datetime.now() # Get the current date and time
        # Insert a new row into the motion_events table with the current timestamp, date, and weather condition
        c.execute("INSERT INTO motion_events (timestamp, date, weather_condition) VALUES (?, ?, ?)",
                  (now.strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d'), weather_condition))
        conn.commit() # Commit the changes
        print(f"Motion event logged at {now} with weather: {weather_condition}")
        conn.close() # Close the connection
    except Exception as e:
        print(f"Error logging motion: {e}")

# Get motion statistics from database
def get_motion_stats():
    try:
        # Connect to the database
        with sqlite3.connect('motion.db') as conn: 
            c = conn.cursor()
            # Get the total number of motion events and the number of events
            total_triggers = c.execute("SELECT COUNT(*) FROM motion_events").fetchone()[0]
            today = datetime.now().strftime('%Y-%m-%d')
            # Get the number of motion events for today only
            today_triggers = c.execute("SELECT COUNT(*) FROM motion_events WHERE date = ?", (today,)).fetchone()[0]
            return {"total": total_triggers, "today": today_triggers}
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {"total": 0, "today": 0}

# Get weather data from OpenWeatherMap API
def get_weather_data(city):
    global current_weather # declare current_weather as a global variable
    params = {"q": city, "appid": API_KEY, "units": "metric"} # Set the parameters for the API request, such as city, API key, and units
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json() # Get the JSON response
        main = data.get('main', {}) # Get the main weather data
        weather = data.get('weather', [{}])[0] # Get the first weather description
        sys = data.get('sys', {})
        dt = data.get('dt') # Get the current time
        sunrise = sys.get('sunrise') # Get the sunrise time
        sunset = sys.get('sunset') # Get the sunset time
        weather_description = weather.get('main')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sunrise_time = datetime.fromtimestamp(sunrise).strftime('%Y-%m-%d %H:%M:%S')
        sunset_time = datetime.fromtimestamp(sunset).strftime('%Y-%m-%d %H:%M:%S')
        danger_zone = True

        current_weather = weather_description

        # Check if it's not daytime (between sunrise and sunset)
        if not (sunrise <= dt <= sunset):
            # Check if it's not dangerzone 
            if not danger_zone:
                if weather_description == "Clear": # If the weather is clear, turn off the light, send waitfor1 which means wait for motion to turn on light to level 1
                    return "waitfor1", True, weather_description
                # if the weather is Rain or Thunderstorm, turn on the light to level 1, waitfor2 which means wait for motion to turn on light to level 2
                elif weather_description in ["Rain", "Thunderstorm"]:
                    return "waitfor2", False, weather_description
                else: # if the weather is not clear, rain or thunderstorm, waitfor1 which means wait for motion to turn on light to level 1
                    return "waitfor1", True, weather_description
            else: # if it's dangerzone
                # if the weather is thunderstorm, rain, mist or snow turn on the light to level 2, lightis2
                if weather_description in ["Thunderstorm", "Rain", "Mist", "Snow"]:
                    return "lightis2", False, weather_description
                else: # else turn on light to level 1 and wait for motion to turn on light to level 2
                    return "waitfor2", False, weather_description
        else: # if it's daytime
            if weather_description == "Clear": # if the weather is clear, turn off the light, lightis0
                return "lightis0", True, weather_description
            # if the weather is thunderstorm or snow, turn on the light to level 2, lightis2
            elif weather_description in ["Thunderstorm", "Snow"]:
                return "lightis2", False, weather_description
            else: # else turn on the light to level 1 and wait for motion to turn on light to level 2
                return "waitfor2", True, weather_description
    return "Error", True, "Error"

def pir_test():
    global light # declare light as a global variable
    weather = get_weather_data("Stockholm") # Get the weather data for Stockholm
    loop = 0 # Set the loop counter to 0
    # run this loop for 60 timess
    while loop <= 60:
        try:
            if weather[0] == "lightis2": # if the weather condition is lightis2
                print("light level is 2 because of weather condition")
                light = "#ffd500" # Set the light color to bright yellow
                # keep track of motions
                try:
                    print("PIR Sensor Ready...")
                    loop2 = 0 # Set the loop counter to 0
                    while loop2 < 25: # run this loop for 25 times to let it run atleast 25 seconds
                        if GPIO.input(PIR_PIN): # if there is motion detected
                            log_motion_event(weather[2]) # Log the motion event with the weather condition
                            time.sleep(25) # if there is a motion detected sleep for 25 seconds to not trigger log_motion_event multiple times
                        else: # if there is no motion detected
                            print("No Motion. turn light off")
                        time.sleep(1) # sleep for 1 second to not get error telling us GPIO is busy
                        loop2 += 1  # increment the loop counter by 1
                except KeyboardInterrupt: # if there is a keyboard interrupt
                    print("Exiting...")
                
            elif weather[0] == "lightis0": # if the weather condition is lightis0
                print("light level is 0 because of no need for light")
                light = "#cccccc" # Set the light color to grey
                try:
                    print("PIR Sensor Ready...")
                    loop2 = 0 # Set the loop counter to 0
                    while loop2 < 25: # run this loop for 25 times to let it run atleast 25 seconds
                        if GPIO.input(PIR_PIN): # if there is motion detected
                            log_motion_event(weather[2]) # Log the motion event with the weather condition
                            time.sleep(25) # if there is a motion detected sleep for 25 seconds to not trigger log_motion_event multiple times
                        else:
                            print("No Motion. turn light off")  # if there is no motion detected
                        time.sleep(1) # sleep for 1 second to not get error telling us GPIO is busy
                        loop2 += 1 # increment the loop counter by 1
                except KeyboardInterrupt: # if there is a keyboard interrupt
                    print("Exiting...")
                
            elif weather[0] == "waitfor1": # if the weather condition is waitfor1
                print("light is off but waiting for motion to turn on lights to level 1") 
                light = "#cccccc" # Set the light color to grey
                try:
                    print("PIR Sensor Ready...")
                    loop2 = 0 # Set the loop counter to 0
                    while loop2 < 25: # run this loop for 25 times to let it run atleast 25 seconds
                        if GPIO.input(PIR_PIN): # if there is motion detected
                            print("Motion Detected! turn on light to level 1") 
                            light = "#fff394" # Set the light color to light yellow
                            log_motion_event(weather[2]) # Log the motion event with the weather condition
                            time.sleep(25) # if there is a motion detected sleep for 25 seconds to not trigger log_motion_event multiple times
                        else:
                            print("No Motion. turn light off") # if there is no motion detected
                            light = "#cccccc" # Set the light color to grey
                        time.sleep(1) # sleep for 1 second to not get error telling us GPIO is busy
                        loop2 += 1 # increment the loop counter by 1
                except KeyboardInterrupt: # if there is a keyboard interrupt
                    print("Exiting...")
                
            else:  # waitfor2
                try:
                    print("PIR Sensor Ready...")
                    loop2 = 0 # Set the loop counter to 0
                    while loop2 < 25: # run this loop for 25 times to let it run atleast 25 seconds
                        if GPIO.input(PIR_PIN): # if there is motion detected
                            print("Motion Detected! turn on light to level 2") 
                            light = "#ffd500" # Set the light color to bright yellow
                            log_motion_event(weather[2]) # Log the motion event with the weather condition
                            time.sleep(25) # if there is a motion detected sleep for 25 seconds to not trigger log_motion_event multiple times
                        else:
                            print("No Motion. turn light level 1")
                            light = "#fff394" # Set the light color to light yellow
                        time.sleep(1) # sleep for 1 second to not get error telling us GPIO is busy
                        loop2 += 1 # increment the loop counter by 1
                except KeyboardInterrupt:
                    print("Exiting...")
            
            loop += 1 # increment the loop counter by 1
            weather = get_weather_data("Stockholm")  # Update weather for next iteration
        except KeyboardInterrupt: # if there is a keyboard interrupt
            print("Exiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

# Background thread to monitor PIR sensor and weather
def background_thread():
    while True:
        pir_test()

# Route to index page
@app.route('/')
def index():
    return render_template('index.html') # Render the index.html template

# Route to get motion stats
@app.route('/get_stats')
def get_stats():
    stats = get_motion_stats() # Get the motion statistics
    # Return the statistics as JSON
    return jsonify({
        'color': light,
        'weather': current_weather,
        'motions_today': stats['today'],
        'motions_total': stats['total']
    })

# Route to get motion data
@app.route('/get_motion_data')
def get_motion_data():
    try:
        # Connect to the database
        with sqlite3.connect('motion.db') as conn:
            c = conn.cursor() 
            # Get all motion events, ordered by timestamp descending (most recent first)
            c.execute("""
                SELECT timestamp, weather_condition 
                FROM motion_events 
                ORDER BY timestamp DESC
            """)
            data = c.fetchall() # Fetch all the data
            # Convert to list of dictionaries
            motion_data = [
                {
                    'timestamp': row[0],
                    'weather_condition': row[1]
                }
                for row in data
            ]
            # Return the motion data as JSON
            return jsonify(motion_data)
    except Exception as e:
        print(f"Error getting motion data: {e}")
        return jsonify([])

# Main function to run the Flask app
if __name__ == '__main__':
    init_db()
    # Start background thread for PIR and weather monitoring
    Thread(target=background_thread, daemon=True).start()
    # Run Flask app
    app.run(host='0.0.0.0', port=5000)