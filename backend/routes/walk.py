import json
import uuid
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from models.db import get_pool, get_redis
from models.schemas import WalkStartRequest, WalkStartResponse, WalkEndRequest, AlertRequest
from services.eta import get_walking_eta
from services.geofence import is_within_home

router = APIRouter()

ALERT_RATE_LIMIT = 3
ALERT_RATE_WINDOW = 30  # seconds


@router.post("/walk/start", response_model=WalkStartResponse)
async def start_walk(body: WalkStartRequest):
    pool = get_pool()
    redis = get_redis()

    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, home_lat, home_lng FROM users WHERE id = $1", 
            uuid.UUID(body.user_id)
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        eta = await get_walking_eta(
            body.current_lat, body.current_lng,
            user["home_lat"], user["home_lng"],
        )

        session_id = await conn.fetchval(
            """
            INSERT INTO walk_sessions (user_id, status, eta_minutes, eta_time)
            VALUES ($1, 'active', $2, $3)
            RETURNING id
            """,
            uuid.UUID(body.user_id), eta["eta_minutes"], eta["eta_time"],
        )

        await conn.execute(
            """
            INSERT INTO walk_events (session_id, event_type, data_shared)
            VALUES ($1, 'walk_started', $2)
            """,
            session_id, f"eta_minutes={eta['eta_minutes']}",
        )

    session_id_str = str(session_id)
    ttl = (eta["eta_minutes"] + 30) * 60

    await redis.set(
        f"walk:{session_id_str}:state",
        "ACTIVE",
        ex=ttl,
    )

    # Store initial location
    location_data = json.dumps({
        "lat": body.current_lat,
        "lng": body.current_lng,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    await redis.set(f"walk:{session_id_str}:location", location_data, ex=ttl)

    return {
        "session_id": session_id_str,
        "eta_minutes": eta["eta_minutes"],
        "eta_time": eta["eta_time"],
    }


@router.post("/walk/end")
async def end_walk(body: WalkEndRequest):
    pool = get_pool()
    redis = get_redis()

    async with pool.acquire() as conn:
        session = await conn.fetchrow(
            "SELECT id, status FROM walk_sessions WHERE id = $1",
            uuid.UUID(body.session_id),
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session["status"] != "active":
            raise HTTPException(status_code=400, detail="Session is not active")

        await conn.execute(
            """
            UPDATE walk_sessions
            SET status = 'safe', ended_at = now()
            WHERE id = $1
            """,
            uuid.UUID(body.session_id),
        )

        await conn.execute(
            """
            INSERT INTO walk_events (session_id, event_type)
            VALUES ($1, 'walk_ended_safe')
            """,
            uuid.UUID(body.session_id),
        )

    # Delete Redis keys immediately — not at TTL expiry
    await redis.delete(f"walk:{body.session_id}:location")
    await redis.delete(f"walk:{body.session_id}:state")
    await redis.delete(f"walk:{body.session_id}:ratelimit")

    return {"status": "safe"}


@router.post("/walk/alert")
async def trigger_alert(body: AlertRequest):
    pool = get_pool()
    redis = get_redis()

    rate_key = f"walk:{body.session_id}:ratelimit"
    current = await redis.get(rate_key)
    count = int(current) if current else 0

    if count >= ALERT_RATE_LIMIT:
        ttl = await redis.ttl(rate_key)
        raise HTTPException(
            status_code=429,
            detail={"error": "Rate limit exceeded", "retry_after": ttl},
        )

    pipe = redis.pipeline()
    pipe.incr(rate_key)
    pipe.expire(rate_key, ALERT_RATE_WINDOW)
    await pipe.execute()

    async with pool.acquire() as conn:
        session = await conn.fetchrow(
            "SELECT id, status FROM walk_sessions WHERE id = $1",
            uuid.UUID(body.session_id),
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        await conn.execute(
            """
            UPDATE walk_sessions SET status = 'escalated' WHERE id = $1
            """,
            uuid.UUID(body.session_id),
        )

        await conn.execute(
            """
            INSERT INTO walk_events (session_id, event_type, data_shared)
            VALUES ($1, 'alert_triggered', $2)
            """,
            uuid.UUID(body.session_id),
            f"type={body.type} confidence={body.confidence}",
        )

    await redis.set(f"walk:{body.session_id}:state", "CONTACT_NOTIFIED")

    return {"status": "escalating"}


@router.get("/walk/history")
async def walk_history(user_id: str):
    pool = get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, started_at, ended_at, status
            FROM walk_sessions
            WHERE user_id = $1
            ORDER BY started_at DESC
            LIMIT 50
            """,
            uuid.UUID(user_id),
        )

    result = []
    for row in rows:
        duration = None
        if row["ended_at"] and row["started_at"]:
            duration = int((row["ended_at"] - row["started_at"]).total_seconds() / 60)
        result.append({
            "session_id": str(row["id"]),
            "date": row["started_at"],
            "duration_minutes": duration,
            "status": row["status"],
        })

    return result


@router.get("/walk/{session_id}/map-token")
async def get_map_token(session_id: str):
    redis = get_redis()

    token = str(uuid.uuid4())
    # Store token mapped to session, valid for 24 hours
    await redis.set(f"maptoken:{token}", session_id, ex=86400)

    return {"token": token}