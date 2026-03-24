import os
from fastapi import APIRouter, HTTPException
from models.db import get_pool, get_redis
from models.schemas import ConsentAcceptRequest, ConsentRevokeRequest, ConsentStatusResponse

router = APIRouter()


@router.get("/consent/{token}", response_model=ConsentStatusResponse)
async def get_consent_status(token: str):
    pool = get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT c.name AS contact_name, u.name AS student_name, c.consent_accepted
            FROM contacts c
            JOIN users u ON u.id = c.user_id
            WHERE c.consent_token = $1
            """,
            token,
        )

    if not row:
        raise HTTPException(status_code=404, detail="Invalid consent token")

    return {
        "student_name": row["student_name"],
        "contact_name": row["contact_name"],
        "already_accepted": row["consent_accepted"],
    }


@router.post("/consent/accept")
async def accept_consent(body: ConsentAcceptRequest):
    pool = get_pool()

    async with pool.acquire() as conn:
        updated = await conn.fetchval(
            """
            UPDATE contacts
            SET consent_accepted = true, consent_accepted_at = now()
            WHERE consent_token = $1
            RETURNING id
            """,
            body.token,
        )

    if not updated:
        raise HTTPException(status_code=404, detail="Invalid consent token")

    return {"status": "accepted"}


@router.post("/consent/revoke")
async def revoke_consent(body: ConsentRevokeRequest):
    pool = get_pool()
    redis = get_redis()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            UPDATE contacts
            SET tracking_active = false
            WHERE consent_token = $1
            RETURNING id, user_id
            """,
            body.token,
        )

    if not row:
        raise HTTPException(status_code=404, detail="Invalid consent token")

    # Signal the contact WebSocket to close if currently connected
    contact_id = str(row["id"])
    await redis.set(f"revoked:{contact_id}", "1", ex=3600)

    return {"status": "revoked"}