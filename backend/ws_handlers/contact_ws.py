import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from models.db import get_pool, get_redis


async def contact_websocket(websocket: WebSocket, session_id: str, map_token: str):
    redis = get_redis()
    pool = get_pool()

    # Validate map token
    token_session = await redis.get(f"maptoken:{map_token}")
    if token_session != session_id:
        await websocket.close(code=4001)
        return

    # Validate consent
    async with pool.acquire() as conn:
        contact = await conn.fetchrow(
            """
            SELECT c.id, c.consent_accepted, c.tracking_active
            FROM contacts c
            JOIN users u ON u.id = c.user_id
            JOIN walk_sessions ws ON ws.user_id = u.id
            WHERE ws.id = $1 AND c.consent_accepted = true AND c.tracking_active = true
            LIMIT 1
            """,
            session_id,
        )

    if not contact:
        await websocket.close(code=4003)
        return

    await websocket.accept()
    contact_id = str(contact["id"])

    try:
        while True:
            # Check if consent was revoked
            revoked = await redis.get(f"revoked:{contact_id}")
            if revoked:
                await websocket.close(code=4003)
                break

            # Check if session is still active
            state = await redis.get(f"walk:{session_id}:state")
            if not state:
                await websocket.send_text(json.dumps({
                    "lat": None,
                    "lng": None,
                    "timestamp": None,
                    "status": "ended",
                }))
                break

            location = await redis.get(f"walk:{session_id}:location")
            if location:
                data = json.loads(location)
                data["status"] = state
                await websocket.send_text(json.dumps(data))

            await asyncio.sleep(3)

    except WebSocketDisconnect:
        pass