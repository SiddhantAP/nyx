import uuid
import os
from fastapi import APIRouter, HTTPException
from twilio.rest import Client

from models.db import get_pool
from models.schemas import UserSetupRequest, UserSetupResponse

router = APIRouter()


def send_consent_sms(contact_name: str, contact_phone: str, student_name: str, token: str):
    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    base_url = os.environ.get("BASE_URL", "")
    link = f"{base_url}/consent/{token}"
    client.messages.create(
        body=(
            f"Hi {contact_name}, {student_name} has added you as a safety contact on Nyx. "
            f"Accept here to receive their live location when they walk home at night: {link}"
        ),
        from_=os.environ["TWILIO_PHONE_NUMBER"],
        to=f"+91{contact_phone}",
    )


@router.post("/users/setup", response_model=UserSetupResponse)
async def setup_user(body: UserSetupRequest):
    pool = get_pool()

    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE phone = $1", body.phone
        )
        if existing:
            raise HTTPException(status_code=400, detail="User with this phone already exists")

        user_id = await conn.fetchval(
            """
            INSERT INTO users (name, phone, home_lat, home_lng)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            body.name, body.phone, body.home_lat, body.home_lng,
        )

        for contact in body.contacts:
            token = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO contacts (user_id, name, phone, consent_token)
                VALUES ($1, $2, $3, $4)
                """,
                user_id, contact.name, contact.phone, token,
            )
            try:
                send_consent_sms(contact.name, contact.phone, body.name, token)
            except Exception as e:
                print(f"SMS failed for {contact.phone}: {e}")

    return {"user_id": str(user_id)}
