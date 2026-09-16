import os
import requests
from dotenv import load_dotenv

load_dotenv()

ORS_API_KEY = os.getenv("ORS_API_KEY")

DIRECTIONS_URL = (
    
    "https://api.heigit.org/openrouteservice/v2/directions/driving-car/geojson"
)


GEOCODE_URL = "https://api.heigit.org/pelias/v1/search"


def get_coordinates(location_name):
    """
    Convert a city/place name into longitude and latitude.
    """

    params = {
        "api_key": ORS_API_KEY,
        "text": f"{location_name}, Maharashtra, India"
    }

    response = requests.get(
        GEOCODE_URL,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        return None

    data = response.json()

    features = data.get("features", [])

    if not features:
        return None

    coordinates = features[0]["geometry"]["coordinates"]

    return coordinates


def get_route(pickup, destination):
    """
    Get driving route information between pickup and destination.
    """

    pickup_coordinates = get_coordinates(pickup)
    destination_coordinates = get_coordinates(destination)

    if pickup_coordinates is None:
        return {
            "pickup": pickup,
            "destination": destination,
            "distance": None,
            "duration": None,
            "route": None,
            "error": f"Could not find pickup location: {pickup}"
        }

    if destination_coordinates is None:
        return {
            "pickup": pickup,
            "destination": destination,
            "distance": None,
            "duration": None,
            "route": None,
            "error": f"Could not find destination: {destination}"
        }

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "coordinates": [
            pickup_coordinates,
            destination_coordinates
        ]
    }

    response = requests.post(
        DIRECTIONS_URL,
        json=data,
        headers=headers,
        timeout=15
    )

    if response.status_code != 200:
        return {
            "pickup": pickup,
            "destination": destination,
            "distance": None,
            "duration": None,
            "route": None,
            "error": response.text
        }

    result = response.json()

    feature = result["features"][0]

    distance_km = feature["properties"]["summary"]["distance"] / 1000
    duration_minutes = feature["properties"]["summary"]["duration"] / 60

    return {
        "pickup": pickup,
        "destination": destination,
        "distance": round(distance_km, 2),
        "duration": round(duration_minutes, 2),
        "route": feature["geometry"]

    
}

    return {
        "pickup": pickup,
        "destination": destination,
        "distance": round(distance_km, 2),
        "duration": round(duration_minutes, 2),
        "route": route["geometry"]
    }