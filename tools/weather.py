import requests


def get_current_weather(user_prompt):

    lowered = user_prompt.lower()

    if "weather in" in lowered:
        city = lowered.split("weather in", 1)[1].strip()
    else:
        return "Sorry, I couldn't tell what city you meant."

    # call the api
    data = get_weather(city)

    if data is None:
        model_reply = f"Sorry, I couldn't retrieve the weather for {city}."
    else:
        temp = data["temperature"]
        wind = data["windspeed"]
        model_reply = f"The current temperature in {city.title()} is {temp}°C with a wind speed of {wind} km/h."
        
    return model_reply


def get_weather(city):
    """Fetch the current weather for a given city."""
    #convert city name to lat and lon cords
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search", 
        params={"name": city}
    ).json()

    if "results" not in geo or len(geo["results"]) == 0:
        return None
    
    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    # fetch weather data using lat and lon cords
    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        }
    ).json()

    if "current_weather" not in weather:
        return None
    
    return weather["current_weather"]
