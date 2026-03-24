import os
from twilio.rest import Client


def get_twilio_client():
    return Client(
        os.environ["TWILIO_ACCOUNT_SID"],   
        os.environ["TWILIO_AUTH_TOKEN"],     
    )


async def send_sms_alert(to_phone: str, message: str):
    """Send an SMS alert to a contact via Twilio."""
    try:
        client = get_twilio_client()
        client.messages.create(
            body=message,
            from_=os.environ["TWILIO_PHONE_NUMBER"],  
            to=f"+91{to_phone}",  
        )
    except Exception as e:
        print(f"SMS send failed to {to_phone}: {e}")


async def notify_contacts_walk_started(contacts: list[dict], student_name: str, session_id: str):
    base_url = os.environ.get("BASE_URL", "")  
    for contact in contacts:
        if not contact["consent_accepted"]:
            continue
        message = (
            f"{student_name} has started walking home. "
            f"Track their live location here: {base_url}/track/{session_id}?token={contact['consent_token']}"
        )
        await send_sms_alert(contact["phone"], message)


async def notify_contacts_safe_arrival(contacts: list[dict], student_name: str):
    for contact in contacts:
        if not contact["consent_accepted"]:
            continue
        message = f"{student_name} has arrived home safely. You can stop tracking."
        await send_sms_alert(contact["phone"], message)


async def notify_contacts_escalation(contacts: list[dict], student_name: str):
    for contact in contacts:
        if not contact["consent_accepted"]:
            continue
        message = (
            f"⚠️ SAFETY ALERT: {student_name} has not arrived home and is not responding. "
            f"Please check on them immediately."
        )
        await send_sms_alert(contact["phone"], message)