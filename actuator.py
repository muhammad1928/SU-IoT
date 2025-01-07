# import requests, json, hashlib, uuid, time 

# privkey = "ZUXEVEGA9USTAZEWRETHAQUBUR69U6EF"
# # token secret
# secret ="ecd6a7203c64ec98469df1da577eeff3"
# pubkey = "FEHUVEW84RAFR5SP22RABURUPHAFRUNU"
# token="8aba8385b6f65e0f7bf274e5e673f04b05d541a1e"
# # Public key:        FEHUVEW84RAFR5SP22RABURUPHAFRUNU

# # Private key:       ZUXEVEGA9USTAZEWRETHAQUBUR69U6EF

# # Token:               8aba8385b6f65e0f7bf274e5e673f04b05d541a1e

# # Token secret:    ecd6a7203c64ec98469df1da577eeff3
# localtime = time.localtime(time.time()) 
# timestamp = str(time.mktime(localtime)) 
# nonce = uuid.uuid4().hex 
# oauthSignature = (privkey + "%26" + secret) 
# # GET-request 
# def turnOn():
#     response = requests.get(
#         url="https://pa-api.telldus.com/json/device/turnOn", 
#         params={  
#             "id": "11504889",  # only for testing but it does not work
#             # "includeValues": "1", 
#             }, 
#             headers={ 
#                 "Authorization": 'OAuth oauth_consumer_key="{pubkey}", oauth_nonce="{nonce}", oauth_signature="{oauthSignature}", oauth_signature_method="PLAINTEXT", oauth_timestamp="{timestamp}", oauth_token="{token}", oauth_version="1.0"'.format(pubkey=pubkey, nonce=nonce, oauthSignature=oauthSignature, timestamp=timestamp, token=token), }, ) 

# def turnOff():
#     response = requests.get(
#         url="https://pa-api.telldus.com/json/device/turnOff", 
#         params={ 
#             "id": "11504889", # only for testing but it does not work
#             # "includeValues": "1", 
#             }, 
#             headers={ 
#                 "Authorization": 'OAuth oauth_consumer_key="{pubkey}", oauth_nonce="{nonce}", oauth_signature="{oauthSignature}", oauth_signature_method="PLAINTEXT", oauth_timestamp="{timestamp}", oauth_token="{token}", oauth_version="1.0"'.format(pubkey=pubkey, nonce=nonce, oauthSignature=oauthSignature, timestamp=timestamp, token=token), }, ) 
    
#     # # Output/response from GET-request  
#     # responseData = response.json() 
#     # # print(responseData) 
#     # print(json.dumps(responseData, indent=4, sort_keys=True)) 

import requests
import json
import time, hashlib, uuid

privkey = "ZUXEVEGA9USTAZEWRETHAQUBUR69U6EF"
secret ="ecd6a7203c64ec98469df1da577eeff3"
pubkey = "FEHUVEW84RAFR5SP22RABURUPHAFRUNU"
token="8aba8385b6f65e0f7bf274e5e673f04b05d541a1e"
localtime = time.localtime(time.time()) 
timestamp = str(time.mktime(localtime)) 
nonce = uuid.uuid4().hex 
oauthSignature = (privkey + "%26" + secret) 

def turnOn():
    response = requests.get(
        url="https://pa-api.telldus.com/json/device/turnOn",
        params={
            "id": "11504889",  # only for testing but it does not work
        },
        headers={
            "Authorization": 'OAuth oauth_consumer_key="{pubkey}", oauth_nonce="{nonce}", oauth_signature="{oauthSignature}", oauth_signature_method="PLAINTEXT", oauth_timestamp="{timestamp}", oauth_token="{token}", oauth_version="1.0"'.format(pubkey=pubkey, nonce=nonce, oauthSignature=oauthSignature, timestamp=timestamp, token=token),
        },
    )

def turnOff():
    response = requests.get(
        url="https://pa-api.telldus.com/json/device/turnOff",
        params={
            "id": "11504889",  # only for testing but it does not work
        },
        headers={
            "Authorization": 'OAuth oauth_consumer_key="{pubkey}", oauth_nonce="{nonce}", oauth_signature="{oauthSignature}", oauth_signature_method="PLAINTEXT", oauth_timestamp="{timestamp}", oauth_token="{token}", oauth_version="1.0"'.format(pubkey=pubkey, nonce=nonce, oauthSignature=oauthSignature, timestamp=timestamp, token=token),
        },
    )





import os
import requests
from flask import Flask, render_template
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# Read API key from api-weather.txt
try:
    with open("../../api-weather.txt", "r") as f:
        API_KEY = f.read().strip()
except FileNotFoundError:
    raise ValueError("API Key file not found. Please create 'api-weather.txt' and add the API key.")

# OpenWeatherMap base URL
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Weather condition to background mapping
WEATHER_BACKGROUND_MAP = {
    "Clear": "#000033",  # Dark blue for clear sky
    "Clouds": "#A9A9A9",  # Light gray for cloudy
    "Rain": "#708090",  # Dark gray for rain
    "Snow": "#FFFFFF",  # White for snow
    "Thunderstorm": "#2F4F4F",  # Dark slate for thunderstorm
    "Mist": "#D3D3D3",  # Light gray for mist
    "Default": "#87CEEB"  # Sky blue as default color
}

# Set up GPIO
PIR_PIN = 12  # Change this to the GPIO pin you're using

def setup_gpio():
    """Sets up the GPIO pin for PIR sensor."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)

def cleanup_gpio():
    """Cleans up GPIO resources."""
    GPIO.cleanup()

def get_motion_status():
    """Checks the current motion sensor status."""
    return GPIO.input(PIR_PIN)

def get_weather_data(city):
    """Fetch weather data and determine background color, description, and reasoning."""
    params = {"q": city, "appid": API_KEY, "units": "metric"}  # Metric units for Celsius
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        weather_data = response.json()
        condition = weather_data["weather"][0]["main"]
        description = weather_data["weather"][0]["description"].capitalize()
        temp = weather_data["main"]["temp"]
        sys_info = weather_data["sys"]
        current_time = weather_data["dt"]
        sunrise = sys_info["sunrise"]
        sunset = sys_info["sunset"]

        # Determine the background color based on time and motion
        if sunrise <= current_time <= sunset:  # Daytime
            # Brighten background if motion is detected
            if get_motion_status():
                background_color = "#FFD700"  # Bright yellow for motion
                reason += " Motion detected, so the background is brighter."
                background_color = WEATHER_BACKGROUND_MAP.get(condition, WEATHER_BACKGROUND_MAP["Default"])
            reason = f"It's daytime with {condition.lower()} weather."
        else:  # Nighttime
            background_color = "#000033"  # Darker background for night
            reason = "It's nighttime, so the background is darker."
        return {
            "background_color": background_color,
            "description": f"{description}, {temp}°C",
            "reason": reason
        }
    return {
        "background_color": WEATHER_BACKGROUND_MAP["Default"],
        "description": "Unable to fetch weather data",
        "reason": "Default color is shown because weather data could not be retrieved."
    }


@app.route("/")
def index():
    city = "Stockholm"  # Stockholm, Sweden by default
    weather_data = get_weather_data(city)
    return render_template(
        "index.html",
        background_color=weather_data["background_color"],
        weather_description=weather_data["description"],
        color_reason=weather_data["reason"]
        )


if __name__ == '__main__':
    try:
        setup_gpio()  # Call setup_gpio before running the app
        app.run(host="0.0.0.0", port=8080, debug=True)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        cleanup_gpio()  # Ensure GPIO cleanup even on exceptions