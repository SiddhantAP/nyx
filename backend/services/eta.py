import os
from datetime import datetime, timedelta
import httpx


async def get_walking_eta(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> dict:
    api_key = os.environ["ORS_API_KEY"]
    url = "https://api.openrouteservice.org/v2/directions/foot-walking"

    headers = {"Authorization": api_key}
    params = {
        "start": f"{origin_lng},{origin_lat}",
        "end": f"{dest_lng},{dest_lat}",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, headers=headers, params=params)

    if response.status_code != 200:
        # Fallback: rough estimate at 5 km/h walking speed
        import math
        dlat = dest_lat - origin_lat
        dlng = dest_lng - origin_lng
        distance_km = math.sqrt(dlat**2 + dlng**2) * 111
        eta_minutes = max(5, int((distance_km / 5) * 60))
        eta_time = datetime.utcnow() + timedelta(minutes=eta_minutes)
        return {"eta_minutes": eta_minutes, "eta_time": eta_time}

    data = response.json()
    duration_seconds = data["features"][0]["properties"]["segments"][0]["duration"]
    eta_minutes = max(1, int(duration_seconds / 60))
    eta_time = datetime.utcnow() + timedelta(minutes=eta_minutes)

    return {"eta_minutes": eta_minutes, "eta_time": eta_time}