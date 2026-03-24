from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContactIn(BaseModel):
    name: str
    phone: str


class UserSetupRequest(BaseModel):
    name: str
    phone: str
    home_lat: float
    home_lng: float
    contacts: list[ContactIn]


class UserSetupResponse(BaseModel):
    user_id: str


class ConsentStatusResponse(BaseModel):
    student_name: str
    contact_name: str
    already_accepted: bool


class ConsentAcceptRequest(BaseModel):
    token: str


class ConsentRevokeRequest(BaseModel):
    token: str


class WalkStartRequest(BaseModel):
    user_id: str
    current_lat: float
    current_lng: float


class WalkStartResponse(BaseModel):
    session_id: str
    eta_minutes: int
    eta_time: datetime


class WalkEndRequest(BaseModel):
    session_id: str


class AlertRequest(BaseModel):
    session_id: str
    type: str  # shake | silent_sos | audio | motion
    confidence: Optional[float] = None


class WalkHistoryItem(BaseModel):
    session_id: str
    date: datetime
    duration_minutes: Optional[int]
    status: str


class MapTokenResponse(BaseModel):
    token: str