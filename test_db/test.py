import sqlite3
from datetime import datetime
import math
import requests
from datetime import datetime
import RPi.GPIO as GPIO
import time

# Initialize database to store motion events with weather
def init_db():
    try:
        conn = sqlite3.connect('motion.db')
        c = conn.cursor()
        # Modify the table to include a new 'weather_condition' column
        c.execute('''CREATE TABLE IF NOT EXISTS motion_events
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp TEXT,
                      date TEXT,
                      weather_condition TEXT)''')
        conn.commit()
        conn.close()
        print("Database initialized successfully")  # Debug print
    except Exception as e:
        print(f"Error initializing database: {e}")  # Debug print

# Log motion event with weather condition
def log_motion_event(weather_condition):
    try:
        conn = sqlite3.connect('motion.db')
        c = conn.cursor()
        now = datetime.now()
        c.execute("INSERT INTO motion_events (timestamp, date, weather_condition) VALUES (?, ?, ?)",
                  (now.strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d'), weather_condition))
        conn.commit()
        print(f"Motion event logged at {now} with weather: {weather_condition}")  # Debug print
        conn.close()
    except Exception as e:
        print(f"Error logging motion: {e}")  # Debug print

def get_motion_stats():
    try:
        with sqlite3.connect('motion.db', timeout=10) as conn:
            c = conn.cursor()
            # Get total triggers
            total_triggers = c.execute("SELECT COUNT(*) FROM motion_events").fetchone()[0]
            # Get today's triggers
            today = datetime.now().strftime('%Y-%m-%d')
            today_triggers = c.execute("SELECT COUNT(*) FROM motion_events WHERE date = ?", (today,)).fetchone()[0]
            print(f"Stats retrieved - Total: {total_triggers}, Today: {today_triggers}")  # Debug print
            return {"total": total_triggers, "today": today_triggers}
    except Exception as e:
        print(f"Error getting stats: {e}")  # Debug print
        return {"total": 0, "today": 0}

# Read API key
try:
    f = open("api.txt", "r")
    API_KEY = f.read().strip()
    f.close()
except FileNotFoundError:
    raise ValueError("API Key file not found. Please create 'api-weather.txt' and add the API key.")


BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

light = "#cccccc"

# setting our algorithm based on weather api
def get_weather_data(city):
    """Fetch weather data and determine background color, description, and reasoning."""
    params = {"q": city, "appid": API_KEY, "units": "metric"}  # Metric units for Celsius
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        sys = data.get('sys', {})
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        temp = main.get('temp')
        weather_description = weather.get('main')
        dt = data.get('dt')
        sunrise = sys.get('sunrise')
        sunset = sys.get('sunset')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sunrise_time = datetime.fromtimestamp(sunrise).strftime('%Y-%m-%d %H:%M:%S')
        sunset_time = datetime.fromtimestamp(sunset).strftime('%Y-%m-%d %H:%M:%S')
        sunrise = sys.get('sunrise')
        dange_zone = True # indicating it is danger zone
        weather_data = {
            "current_time": current_time,
            "temperature": temp,
            "weather": weather_description,
            "sunrise": sunrise_time,
            "sunset": sunset_time,
            "current_time": current_time,
            "danger_Zone": dange_zone
        }
        if not (sunrise <= dt <= sunset): # indicating it is not between sunrise and sunset
            if not(dange_zone): # indicating it is not danger zones
                if weather_description == "Clear": # indicating it is clear sky
                    lights_off = True
                    a = "light is off cuz no danger zone and it is clear sky"
                    a = "waitfor1"
                    return a, lights_off, weather_description
                elif (weather_description == "Rain") or (weather_description == "Thunderstorm"):
                    lights_off = False
                    a = "it is raining so light level is 1 wait for motion to turn on lights to level 2"
                    a = "waitfor2"
                    return a, lights_off, weather_description
                else: # it is cloudy, snowing or mist
                    lights_off = True
                    a = "it is cloudy, snowing or mist so wait for motion to turn on lights to level 1"
                    a = "waitfor1"
                    return a, lights_off, weather_description
            else: # it is danger zone
                if (weather_description == "Thunderstorm") or (weather_description == "Rain") or (weather_description == "Mist") or (weather_description == "Snow"): # if the weather is thunderstorm, rain or mist then light level is 2
                    lights_off = False
                    a = "it is thunderstorm so light level is 2 "
                    a = "lightis2"
                    return a, lights_off, weather_description
                else: # it is danger zone but not thunderstorm, snow,  rain or mist
                    lights_off = False
                    a = "light is always on level 1 cuz it is danger zone and it is night time. waiting for motion for light level 2"
                    a = "waitfor2"
                    return a, lights_off, weather_description
        else: # it is day time
            if weather_description == "Clear": # indicating it is clear sky
                lights_off = True
                a = "light is off cuz no danger zone and it is day time and clear sky"
                a = "lightis0"
                return a, lights_off, weather_description
            elif (weather_description == "Thunderstorm") or (weather_description =="Snow"): # if the weather is snow or thunderstorm then light level is 2
                lights_off = False
                a = "it is raining so light level is 2"
                a = "lightis2"
                return a, lights_off, weather_description
            else: # it is cloudy, snowing, mist or raining
                lights_off = True
                a = "it is cloudy or mist so wait for motion to turn on lights to level 1"
                a = "waitfor2"
                return a, lights_off, weather_description
    else:
        return("Error:", response.status_code, response.text)



# declaring our algorithm to the background color
def pir_test():
    
    weather = get_weather_data("Stockholm") # get the weather data
    global light 
    loop = 0
    while loop<= 5: # continuous loop for motion detection and weather checks
        # Set up GPIO
        PIR_PIN = 12  # Change this to the GPIO pin you're using
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIR_PIN, GPIO.IN)
        try: 
            if weather[0] == "lightis2": # light level is 2
                print("light level is 2 because of weather condition") 
                light = "#ffd500"
                try:
                    loop2 = 0
                    while loop2 < 25: # continuous loop for motion detection and weather checks
                        if GPIO.input(PIR_PIN):
                            log_motion_event(weather[2]) # log the motion event
                            time.sleep(25) # wait for 22 seconds to let our pir reset
                        else:
                            print("No Motion. turn light off") # light off
                        time.sleep(1)
                        loop2 += 1
                except KeyboardInterrupt:
                    print("Exiting...")
                finally:
                    GPIO.cleanup()
            elif weather[0] == "lightis0": # light level is 0 no need for light
                print("light level is 0 because of no need for light")
                light = "#cccccc"
                # check for motion to just keep track of motion even when there is no light
                try:
                    loop2 = 0
                    while loop2 < 25: # continuous loop for motion detection and weather checks
                        if GPIO.input(PIR_PIN):
                            log_motion_event(weather[2]) # log the motion event
                            time.sleep(25) # wait for 22 seconds to let our pir reset
                        else:
                            print("No Motion. turn light off") # light off
                        time.sleep(1)
                        loop2 += 1
                except KeyboardInterrupt:
                    print("Exiting...")
                finally:
                    GPIO.cleanup()
            elif weather[0] == "waitfor1": # light is off but waiting for motion to turn on lights to level 1
                print("light is off but waiting for motion to turn on lights to level 1") 
                light = "#cccccc"
                try:
                    loop2 = 0
                    while loop2 < 25: # continuous loop for motion detection and weather checks
                        if GPIO.input(PIR_PIN):
                            print("Motion Detected! turn on light to level 1") # light level 1
                            light = "#fff394"
                            log_motion_event(weather[2]) # log the motion event
                            time.sleep(25) # wait for 22 seconds to let our pir reset
                        else:
                            print("No Motion. turn light off") # light off
                            light = "#cccccc"
                        time.sleep(1)
                        loop2 += 1
                except KeyboardInterrupt:
                    print("Exiting...")
                finally:
                    GPIO.cleanup()
            else: # light is on level 1 and waiting for motion to turn on lights to level 2
                try:
                    loop2 = 0
                    while loop2 < 25: # continuous loop for motion detection and weather checks
                        if GPIO.input(PIR_PIN):
                            print("Motion Detected! turn on light to level 2") # light level 2
                            light = "#ffd500"
                            log_motion_event(weather[2]) # log the motion event
                            time.sleep(25) # wait for 22 seconds to let our pir reset
                        else:
                            print("No Motion. turn light level 1") # light level 1
                        time.sleep(1)
                        loop2 += 1
                except KeyboardInterrupt:
                    print("Exiting...")
                finally:
                    GPIO.cleanup()
            loop += 1
            # time.sleep(1) # wait for 1 second
        except KeyboardInterrupt:
            print("Exiting...")
            break  # Break the loop to exit gracefully
        except Exception as e:
            print(f"An error occurred: {e}")
            break


def start():
    init_db()
    
    pir_test()
    get_motion_stats()

start()