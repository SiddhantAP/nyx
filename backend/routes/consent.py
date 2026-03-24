from fastapi import APIRouter

router = APIRouter()


@router.get("/consent/{token}")
async def get_consent(token: str):
    return {"student_name": "", "contact_name": "", "already_accepted": False}


@router.post("/consent/accept")
async def accept_consent(body: dict):
    return {"status": "accepted"}


@router.post("/consent/revoke")
async def revoke_consent(body: dict):
    return {"status": "revoked"}