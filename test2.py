import requests
from datetime import datetime
try:
    f = open("../api-weather.txt", "r")
    API_KEY = f.read().strip()
    f.close()
except FileNotFoundError:
    raise ValueError("API Key file not found. Please create 'api-weather.txt' and add the API key.")


BASE_URL = "https://api.openweathermap.org/data/2.5/weather"




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
                if (weather_description == "Thunderstorm") or (weather_description == "Rain") or (weather_description == "Mist"): # if the weather is thunderstorm, rain or mist then light level is 2
                    lights_off = False
                    a = "it is thunderstorm so light level is 2 "
                    a = "lightis2"
                    return a, lights_off
                else: # it is danger zone but not thunderstorm, rain or mist
                    lights_off = True
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

a = get_weather_data("Stockholm")
print(a)

# print(get_weather_data("Stockholm"))