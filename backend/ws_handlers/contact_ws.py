import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from models.db import get_pool, get_redis


async def contact_websocket(websocket: WebSocket, session_id: str, map_token: str):
    redis = get_redis()
    pool = get_pool()

    token_session = await redis.get(f"maptoken:{map_token}")
    print(f"DEBUG: map_token={map_token} token_session={token_session} session_id={session_id}")
    
    if token_session != session_id:
        print(f"DEBUG: token mismatch, closing 4001")
        await websocket.close(code=4001)
        return

    async with pool.acquire() as conn:
        # Check session exists
        session = await conn.fetchrow(
            "SELECT id, user_id FROM walk_sessions WHERE id = $1::uuid",
            session_id,
        )
        print(f"DEBUG: session={session}")

        # Check contacts for this user
        if session:
            contacts = await conn.fetch(
                "SELECT id, consent_accepted, tracking_active FROM contacts WHERE user_id = $1",
                session["user_id"],
            )
            print(f"DEBUG: contacts={[dict(c) for c in contacts]}")

        contact = await conn.fetchrow(
            """
            SELECT c.id, c.consent_accepted, c.tracking_active
            FROM contacts c
            JOIN users u ON u.id = c.user_id
            JOIN walk_sessions ws ON ws.user_id = u.id
            WHERE ws.id = $1::uuid
            AND c.consent_accepted = true
            AND c.tracking_active = true
            LIMIT 1
            """,
            session_id,
        )
        print(f"DEBUG: contact={contact}")

    if not contact:
        print(f"DEBUG: no contact found, closing 4003")
        await websocket.close(code=4003)
        return

    await websocket.accept()
    contact_id = str(contact["id"])

    try:
        while True:
            revoked = await redis.get(f"revoked:{contact_id}")
            if revoked:
                await websocket.close(code=4003)
                break

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