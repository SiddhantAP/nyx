from fastapi import APIRouter
from models.schemas import UserSetupRequest, UserSetupResponse

router = APIRouter()


@router.post("/users/setup", response_model=UserSetupResponse)
async def setup_user(body: UserSetupRequest):
    return {"user_id": "placeholder"}