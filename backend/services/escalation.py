import asyncio
import json
from datetime import datetime, timezone
from models.db import get_pool, get_redis
from services.notifications import notify_contacts_escalation, notify_contacts_safe_arrival


ESCALATION_STATES = [
    "ACTIVE",
    "MISSED_ETA",
    "CHECKIN_SENT",
    "CONTACT_NOTIFIED",
    "SMS_SENT",
    "ESCALATED",
]


async def get_consented_contacts(conn, session_id: str) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT name, phone, consent_token, consent_accepted
        FROM contacts
        WHERE user_id = (
            SELECT user_id FROM walk_sessions WHERE id = $1
        )
        AND consent_accepted = true
        AND tracking_active = true
        """,
        session_id,
    )
    return [dict(r) for r in rows]


async def log_event(conn, session_id: str, event_type: str, data_shared: str = None, recipient: str = None):
    await conn.execute(
        """
        INSERT INTO walk_events (session_id, event_type, data_shared, recipient)
        VALUES ($1, $2, $3, $4)
        """,
        session_id, event_type, data_shared, recipient,
    )


async def run_escalation(session_id: str, eta_minutes: int):
    """
    Runs the escalation state machine for a walk session.
    Called as a background task when a walk starts.
    """
    redis = get_redis()
    pool = get_pool()

    # Wait until ETA + 2 minute buffer
    await asyncio.sleep((eta_minutes * 60) + 120)

    state = await redis.get(f"walk:{session_id}:state")
    if state != "ACTIVE":
        return

    # MISSED_ETA — send WebSocket check-in to student
    await redis.set(f"walk:{session_id}:state", "MISSED_ETA")
    async with pool.acquire() as conn:
        await log_event(conn, session_id, "missed_eta")

    await asyncio.sleep(60)

    state = await redis.get(f"walk:{session_id}:state")
    if state != "MISSED_ETA":
        return

    # CHECKIN_SENT — notify consented contacts
    await redis.set(f"walk:{session_id}:state", "CHECKIN_SENT")
    async with pool.acquire() as conn:
        await log_event(conn, session_id, "checkin_sent")
        contacts = await get_consented_contacts(conn, session_id)
        student = await conn.fetchrow(
            "SELECT u.name FROM users u JOIN walk_sessions ws ON ws.user_id = u.id WHERE ws.id = $1",
            session_id,
        )

    await notify_contacts_escalation(contacts, student["name"])

    await asyncio.sleep(120)

    state = await redis.get(f"walk:{session_id}:state")
    if state != "CHECKIN_SENT":
        return

    # CONTACT_NOTIFIED — send Twilio SMS
    await redis.set(f"walk:{session_id}:state", "CONTACT_NOTIFIED")
    async with pool.acquire() as conn:
        await log_event(conn, session_id, "contact_notified")

    await asyncio.sleep(180)

    state = await redis.get(f"walk:{session_id}:state")
    if state != "CONTACT_NOTIFIED":
        return

    # SMS_SENT — final escalation
    await redis.set(f"walk:{session_id}:state", "SMS_SENT")
    async with pool.acquire() as conn:
        await log_event(conn, session_id, "sms_sent_escalated")
        await conn.execute(
            "UPDATE walk_sessions SET status = 'escalated' WHERE id = $1",
            session_id,
        )