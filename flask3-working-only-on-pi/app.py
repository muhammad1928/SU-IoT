# from flask import Flask, render_template, jsonify, request
# import requests
# from datetime import datetime
# import RPi.GPIO as GPIO
# import time
# import threading

# app = Flask(__name__)

# # Global variables
# light_status = "#cccccc"
# current_weather = None
# motion_detected = False
# test_mode = False
# test_weather = None
# is_day = True
# danger_zone = True  # You can set this based on your criteria

# try:
#     with open("api.txt", "r") as f:
#         API_KEY = f.read().strip()
# except FileNotFoundError:
#     raise ValueError("API Key file not found. Please create 'api.txt' and add the API key.")
# # Set up GPIO
# PIR_PIN = 12  # Change this to the GPIO pin you're using

# BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# def calculate_light_status(weather_desc, is_daytime, has_motion):
#     """Calculate light status based on conditions"""
#     if is_daytime:
#         # Daytime logic
#         if weather_desc == "Clear":
#             return "#cccccc"  # Always off during day if clear
#         elif weather_desc in ["Thunderstorm", "Snow"]:
#             return "#ffd500"  # Always level 2 during day if thunderstorm/snow
#         else:  # Mist, Clouds, etc.
#             return "#ffd500" if has_motion else "#fff394"
#     else:
#         # Nighttime logic
#         if not danger_zone:
#             if weather_desc == "Clear":
#                 return "#fff394" if has_motion else "#cccccc"
#             elif weather_desc in ["Rain", "Thunderstorm"]:
#                 return "#ffd500" if has_motion else "#fff394"
#             else:  # Cloudy, Mist, Snow
#                 return "#ffd500" if has_motion else "#fff394"
#         else:
#             if weather_desc in ["Thunderstorm", "Mist", "Snow", "Rain"]:
#                 return "#ffd500"  # Always level 2
#             else:
#                 return "#ffd500" if has_motion else "#fff394"

# def get_weather_data(city):
#     """Fetch weather data and return formatted response"""
#     global test_mode, test_weather, is_day
    
#     if test_mode and test_weather:
#         return {
#             "temperature": 20,
#             "weather": test_weather,
#             "description": test_weather.lower(),
#             "sunrise": "06:00",
#             "sunset": "18:00"
#         }
    
#     params = {"q": city, "appid": API_KEY, "units": "metric"}
#     response = requests.get(BASE_URL, params=params)
#     if response.status_code == 200:
#         data = response.json()
#         sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
#         sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
        
#         # Update is_day based on current time
#         current_time = datetime.now()
#         sunrise_time = datetime.strptime(sunrise, '%H:%M').replace(
#             year=current_time.year, month=current_time.month, day=current_time.day)
#         sunset_time = datetime.strptime(sunset, '%H:%M').replace(
#             year=current_time.year, month=current_time.month, day=current_time.day)
#         is_day = sunrise_time <= current_time <= sunset_time
        
#         return {
#             "temperature": data['main']['temp'],
#             "weather": data['weather'][0]['main'],
#             "description": data['weather'][0]['description'],
#             "sunrise": sunrise,
#             "sunset": sunset
#         }
#     return None

# def update_system_status():
#     """Update system status based on weather and motion"""
#     global light_status, current_weather, motion_detected
    
#     while True:
#         current_weather = get_weather_data("Stockholm")
#         if current_weather:
#             light_status = calculate_light_status(
#                 current_weather["weather"], 
#                 is_day, 
#                 motion_detected
#             )
#         time.sleep(1)

# def monitor_motion():
#     """Monitor PIR sensor"""
#     global motion_detected
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(PIR_PIN, GPIO.IN)
    
#     while True:
#         if not test_mode:
#             motion_detected = GPIO.input(PIR_PIN)
#         time.sleep(0.1)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/api/status')
# def get_status():
#     return jsonify({
#         'light_status': light_status,
#         'weather': current_weather,
#         'motion': motion_detected,
#         'is_day': is_day,
#         'danger_zone': danger_zone
#     })

# @app.route('/api/test-weather', methods=['POST'])
# def test_weather_endpoint():
#     global test_mode, test_weather
#     test_mode = True
#     test_weather = request.json.get('weather')
#     return jsonify({'status': 'success'})

# @app.route('/api/test-motion', methods=['POST'])
# def test_motion_endpoint():
#     global motion_detected, test_mode
#     test_mode = True
#     motion_detected = request.json.get('motion', False)
#     return jsonify({'status': 'success'})

# if __name__ == '__main__':
#     # Start background threads
#     weather_thread = threading.Thread(target=update_system_status, daemon=True)
#     motion_thread = threading.Thread(target=monitor_motion, daemon=True)
#     weather_thread.start()
#     motion_thread.start()
    
#     try:
#         app.run(host='0.0.0.0', port=5000, debug=True)
#     finally:
#         GPIO.cleanup()


from flask import Flask, render_template

app = Flask(__name__)

light_status = {
    "light_level": "Off",
    "color": "#cccccc",
    "motion_detected": False,
    "manual_weather": None,  # For manual weather testing
    "previous_light_level": "Off",
    "previous_color": "#cccccc",
}

# Route for the homepage
@app.route("/")
def index():
    return render_template("index.html", light_status=light_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

