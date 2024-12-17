f = open("../../api-weather.txt", "r")
print(f.read())


f = open("../../api-weather.txt", "r")


# OpenWeatherMap API Key and Endpoint
API_KEY = f.read()
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"