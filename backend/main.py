from fastapi import FastAPI, File, Response, Cookie, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from youtube_downloader import download_audio
from transcriber import transcribe_audio
from embedder import split_text, create_vectorstore
from agent import create_agent
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict
from uuid import uuid4

from db_model import *

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    chat_id: str
    user_message: str


chat_sessions: Dict[str, Dict] = {}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    audio.file.seek(0)
    transciption = OpenAI().audio.transcriptions.create(
        model="whisper-1", file=(audio.filename, audio.file, audio.content_type)
    )
    return {"text": transciption.text}


@app.post("/chat")
async def chat_endpoint(msg: Message):
    chat_id = msg.chat_id
    user_input = msg.user_message

    agent = create_agent(chat_id)
    agent_reply = agent.run(user_input)
    save_message(chat_id, "user", user_input)
    save_message(chat_id, "agent", agent_reply)
    return {"response": agent_reply, "id": str(uuid4())}


@app.get("/start")
async def start_chat(response: Response, user_id: str = Cookie(default=None)):
    if not user_id:
        user_id = str(uuid4())
        response.set_cookie(key="user_id", value=user_id)
    create_user_if_not_exist(user_id)
    chat_id = create_new_chat(user_id)
    return {"chat_id": chat_id}


@app.get("/user_chats")
async def user_chats(user_id: str = Cookie(default=None)):
    if not user_id:
        return JSONResponse(status_code=400, content={"error": "No user cookie set"})
    return get_user_chats(user_id)


@app.get("/chat_history/{chat_id}")
async def chat_history(chat_id: str):
    history = get_chat_history(chat_id)
    if not history:
        return JSONResponse(
            status_code=404, content={"error": "Chat history not found"}
        )
    return {"chat_id": chat_id, "history": history}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
