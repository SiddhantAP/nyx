import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models.db import init_db, close_db
from routes import users, consent, walk, history
from ws_handlers.student_ws import student_websocket
from ws_handlers.contact_ws import contact_websocket

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="Nyx Safety API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(consent.router)
app.include_router(walk.router)
app.include_router(history.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws/walk/{session_id}")
async def ws_student(websocket: WebSocket, session_id: str):
    await student_websocket(websocket, session_id)


@app.websocket("/ws/contact/{session_id}")
async def ws_contact(websocket: WebSocket, session_id: str, token: str):
    await contact_websocket(websocket, session_id, token)