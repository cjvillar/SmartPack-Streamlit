import requests
import pandas as pd
import json
import time

BASE_URL = "https://api.weather.gov/points/"

# Get Parks
with open("california_parks.json", "r") as f:
    PARKS = json.load(f)


def get_forecast(latitude, longitude):
    """Fetches forecast data for a specific Lat/Lon."""
    url = f"{BASE_URL}{latitude},{longitude}"

    print(f"Fetching point forecast URL: {url}")

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch {response.status_code}")

    data = response.json()
    forcast_url = data["properties"]["forecast"]

    # fetch data from weather.gov
    forecast_resp = requests.get(forcast_url)

    if forecast_resp.status_code != 200:
        print(f"Failed to fetch forecast data: {forecast_resp.status_code}")
        return None

    forecast_data = forecast_resp.json()
    periods = forecast_data["properties"]["periods"]

    forecast_list = []
    for p in periods:
        forecast_list.append(
            {
                "startTime": p["startTime"],
                "Time of Day": p["name"],
                "shortForecast": p["shortForecast"],
                "detailedForecast": p["detailedForecast"],
                "Temp": p["temperature"],
                "Wind": p["windSpeed"].replace(" mph", ""),
                "windDirection": p["windDirection"],
                "Rain": p["probabilityOfPrecipitation"]["value"],
            }
        )

    return forecast_list


def get_gear_recommendations(forecast_list):
    "Recommend Gear based on weather, TODO"
    recommendations = set()
    warnings = []

    # extract lists
    temps = [p["Temp"] for p in forecast_list if p["Temp"] is not None]
    rain = [p["Rain"] for p in forecast_list if p["Rain"] is not None]

    min_temp = min(temps)
    max_rain = max(rain)

    # Temp logic
    if min_temp < 32:
        recommendations.update(
            [
                "❄️ 0°F Rated Sleeping Bag",
                "🧤 Insulated Gloves & Beanie",
                "🔥 Sleeping Pad with R-value > 4",
            ]
        )
        warnings.append("Freezing conditions expected! Bring extra fuel.")
    elif min_temp < 50:
        recommendations.update(["🛌 20°F Rated Sleeping Bag", "🧥 Puffy Down Jacket"])
    else:
        recommendations.add("🏞️ 40°F+ Summer Sleeping Bag")

    # Rain logic
    if max_rain > 0:
        recommendations.update(
            [
                "☔ Waterproof Rainfly",
                "🥾 Waterproof Hiking Boots",
                "🎒 Pack Rain Cover",
            ]
        )
    if max_rain > 50:
        warnings.append(
            "Heavy rain forecast. Ensure tent footprint is tucked under tent."
        )

    return list(recommendations), warnings


def run_weekly_update(output_file="weekly_forecasts.json"):
    all_parks_data = {}

    for park in PARKS:
        name = park["name"]
        lat = park["latitude"]
        lon = park["longitude"]

        print(f"\n=== {name} ===")
        forecast_list = get_forecast(lat, lon)

        if forecast_list is None:
            print(f"No forecast for {name}")
            continue

        # recommendation logic
        gear, warnings = get_gear_recommendations(forecast_list)

        # Add to master structure
        all_parks_data[name] = {
            "latitude": lat,
            "longitude": lon,
            "forecast": forecast_list,
            "recommended_gear": gear,
            "warnings": warnings,
        }

        # Slow down to avoid overwhelming API
        time.sleep(2)

    # Save data to one JSON file
    with open(output_file, "w") as f:
        json.dump(all_parks_data, f, indent=4)


if __name__ == "__main__":
    run_weekly_update()
