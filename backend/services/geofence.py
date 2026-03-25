import math


async def is_within_home(conn, session_id: str, current_lat: float, current_lng: float) -> bool:
    row = await conn.fetchrow(
        """
        SELECT u.home_lat, u.home_lng
        FROM walk_sessions ws
        JOIN users u ON u.id = ws.user_id
        WHERE ws.id = $1
        """,
        session_id,
    )

    if not row:
        return False

    # Haversine distance in metres
    lat1, lng1 = math.radians(current_lat), math.radians(current_lng)
    lat2, lng2 = math.radians(row["home_lat"]), math.radians(row["home_lng"])

    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    distance_metres = 6371000 * 2 * math.asin(math.sqrt(a))

    return distance_metres <= 100