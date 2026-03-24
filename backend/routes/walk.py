from fastapi import APIRouter

router = APIRouter()


@router.post("/walk/start")
async def start_walk(body: dict):
    return {"session_id": "", "eta_minutes": 0, "eta_time": None}


@router.post("/walk/end")
async def end_walk(body: dict):
    return {"status": "safe"}


@router.post("/walk/alert")
async def alert(body: dict):
    return {"status": "escalating"}


@router.get("/walk/history")
async def history(user_id: str):
    return []


@router.get("/walk/{session_id}/map-token")
async def map_token(session_id: str):
    return {"token": ""}