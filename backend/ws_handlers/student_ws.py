import json
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect
from models.db import get_redis


async def student_websocket(websocket: WebSocket, session_id: str):
    redis = get_redis()

    state = await redis.get(f"walk:{session_id}:state")
    if not state:
        await websocket.close(code=4004)
        return

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            lat = payload.get("lat")
            lng = payload.get("lng")
            timestamp = payload.get("timestamp", datetime.now(timezone.utc).isoformat())

            if lat is None or lng is None:
                continue

            location = json.dumps({"lat": lat, "lng": lng, "timestamp": timestamp})
            current_state = await redis.get(f"walk:{session_id}:state")

            if not current_state:
                await websocket.send_text(json.dumps({
                    "type": "safe",
                    "message": "Walk session has ended.",
                }))
                break

            # Refresh TTL on each location update
            ttl = await redis.ttl(f"walk:{session_id}:state")
            await redis.set(f"walk:{session_id}:location", location, ex=max(ttl, 300))

            # If escalation is waiting for a check-in response, reset to ACTIVE
            if current_state == "MISSED_ETA":
                await redis.set(f"walk:{session_id}:state", "ACTIVE")
                await websocket.send_text(json.dumps({
                    "type": "checkin",
                    "message": "Check-in received. Stay safe!",
                }))
            else:
                await websocket.send_text(json.dumps({
                    "type": "checkin",
                    "message": "Location updated.",
                }))

    except WebSocketDisconnect:
        pass