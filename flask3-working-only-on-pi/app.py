import requests
from datetime import datetime
import RPi.GPIO as GPIO
import time
from flask import Flask, render_template, jsonify, request

app = Flask(__name__) 

try:
    f = open("api.txt", "r")
    API_KEY = f.read().strip()
    f.close()
except FileNotFoundError:
    raise ValueError("API Key file not found. Please create 'api-weather.txt' and add the API key.")


BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
light_settings = {
    "light": "#cccccc",
    "manual_weather": None,
    "previous_light_level": "Off"
}

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
                    return a, lights_off
                elif (weather_description == "Rain") or (weather_description == "Thunderstorm"):
                    lights_off = False
                    a = "it is raining so light level is 1 wait for motion to turn on lights to level 2"
                    a = "waitfor2"
                    return a, lights_off
                else: # it is cloudy, snowing or mist
                    lights_off = True
                    a = "it is cloudy, snowing or mist so wait for motion to turn on lights to level 1"
                    a = "waitfor1"
                    return a, lights_off 
            else: # it is danger zone
                if (weather_description == "Thunderstorm") or (weather_description == "Rain") or (weather_description == "Mist") or (weather_description == "Snow"): # if the weather is thunderstorm, rain or mist then light level is 2
                    lights_off = False
                    a = "it is thunderstorm so light level is 2 "
                    a = "lightis2"
                    return a, lights_off
                else: # it is danger zone but not thunderstorm, snow,  rain or mist
                    lights_off = False
                    a = "light is always on level 1 cuz it is danger zone and it is night time. waiting for motion for light level 2"
                    a = "waitfor2"
                    return a, lights_off
        else: # it is day time
            if weather_description == "Clear": # indicating it is clear sky
                lights_off = True
                a = "light is off cuz no danger zone and it is day time and clear sky"
                a = "lightis0"
                return a, lights_off
            elif (weather_description == "Thunderstorm") or (weather_description =="Snow"): # if the weather is snow or thunderstorm then light level is 2
                lights_off = False
                a = "it is raining so light level is 2"
                a = "lightis2"
                return a, lights_off
            else: # it is cloudy, snowing, mist or raining
                lights_off = True
                a = "it is cloudy or mist so wait for motion to turn on lights to level 1"
                a = "waitfor2"
                return a, lights_off
    else:
        return("Error:", response.status_code, response.text)


# Set up GPIO
PIR_PIN = 12  # Change this to the GPIO pin you're using
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
def pir_test():
    weather = get_weather_data("Stockholm") # get the weather data
    global light 
    if weather[0] == "lightis2": # light level is 2
        print("light level is 2 because of weather condition") 
        light = "#ffd500"
    elif weather[0] == "lightis0": # light level is 0 no need for light
        print("light level is 0 because of no need for light")
        light = "#cccccc"
    elif weather[0] == "waitfor1": # light is off but waiting for motion to turn on lights to level 1
        print("light is off but waiting for motion to turn on lights to level 1") 
        light = "#cccccc"
        try:
            print("PIR Sensor Ready...")
            while True:
                for i in range(5): # loop it for 10 minutes to reduce api usage
                    if GPIO.input(PIR_PIN):
                        print("Motion Detected! turn on light to level 1") # light level 1
                        light = "#fff394"
                    else:
                        print("No Motion. turn light off") # light off
                        light = "#cccccc"
                    time.sleep(1)
                    i += 1
                    print(i)
                print("calling pirtest again 1")
                pir_test()  # recall this function to check the weather again after 10 minutes
                print("calling pirtest again 2")
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            GPIO.cleanup()
    else: # light is on level 1 and waiting for motion to turn on lights to level 2
        try:
            print("PIR Sensor Ready...")
            while True:
                for i in range(5): # loop it for 10 minutes to reduce api usage
                    if GPIO.input(PIR_PIN):
                        print("Motion Detected! turn on light to level 2") # light level 2
                        light = "#ffd500"
                    else:
                        print("No Motion. turn light level 1") # light level 1
                    time.sleep(1)
                    i += 1
                    print(i)
                print("calling pirtest again 1")
                pir_test() # recall this function to check the weather again after 10 minutes
                print("calling pirtest again 2")
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            GPIO.cleanup()
    
                
pir_test()
