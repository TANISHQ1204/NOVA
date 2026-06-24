import requests
import json

def get_weather(city):
    try:
        url=f"https://wttr.in/{city}?format=j1"
        response=requests.get(url, timeout=5)
        if response.status_code!=200:
            return None
        data=response.json()
        

        temp=data["current_condition"][0]["temp_C"]
        feels_like=data["current_condition"][0]["FeelsLikeC"]
        description=data["current_condition"][0]["weatherDesc"][0]["value"]
        humidity=data["current_condition"][0]["humidity"]

        return{
            "temperature": temp,
            "feels_like": feels_like,
            "description": description,
            "humidity": humidity,
        }
    
    except requests.exceptions.Timeout:
        print("Request timed out - server took too long")
        return None
    except requests.exceptions.ConnectionError:
        print("No internet connection")
        return None
    except KeyError as e:
        print(f"Unexpected response format. Missing key: {e}")
        return None
