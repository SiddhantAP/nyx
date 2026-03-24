async def is_within_home(conn, session_id: str, current_lat: float, current_lng: float) -> bool:
    row = await conn.fetchrow(
        """
        SELECT ST_DWithin(
            ST_MakePoint($1, $2)::geography,
            ST_MakePoint(u.home_lng, u.home_lat)::geography,
            100
        ) AS arrived
        FROM walk_sessions ws
        JOIN users u ON u.id = ws.user_id
        WHERE ws.id = $3
        """,
        current_lng, current_lat, session_id,
    )

    if not row:
        return False

    return row["arrived"]

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImUyMDU0MmEzMzRjODQ0YmE4NjJjMDc1OTg3MDQ1ZmVmIiwiaCI6Im11cm11cjY0In0="