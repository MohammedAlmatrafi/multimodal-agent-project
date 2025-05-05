from fastapi import FastAPI, Response, Cookie
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.post("/process_video/")
# async def process_video(url: str):
#     audio_path = download_audio(url)
#     transcript = transcribe_audio(audio_path)
#     chunks = split_text(transcript)
#     create_vectorstore(chunks)
#     global agent
#     agent = create_agent()
#     return {"message": "Video processed and agent ready."}


class Message(BaseModel):
    chat_id: str
    user_message: str


chat_sessions: Dict[str, Dict] = {}


# @app.post("/chat")
# async def chat(msg: Message):
#     chat_id = msg.chat_id
#     user_msg = msg.user_message

#     if chat_id not in chat_sessions:
#         # Create new chat memory and vectorstore
#         chat_sessions[chat_id] = {
#             "history": [],
#             "vectorstore": [],  # Replace with Faiss/Chroma/etc.
#         }

#     session = chat_sessions[chat_id]
#     session["history"].append({"role": "user", "content": user_msg})

#     # Replace below with real agent response
#     # agent = create_agent()
#     # agent_response = agent.run(user_msg)
#     agent_response = f"echo: {user_msg}"
#     session["history"].append({"role": "agent", "content": agent_response})

#     return {"response": agent_response}


@app.post("/chat")
async def chat_endpoint(msg: Message):
    chat_id = msg.chat_id
    user_input = msg.user_message

    # # Step 1: Optional video transcription if needed
    # youtube_url = extract_youtube_url(user_input)
    # if youtube_url:
    #     transcribe_and_save(chat_id, youtube_url)  # adds to vectorstore and DB

    # Step 2: Create agent with loaded memory and vectorstore
    agent = create_agent(chat_id)

    # Step 3: Agent generates reply
    agent_reply = agent.run(user_input)

    # Step 4: Save conversation to DB
    save_message(chat_id, "user", user_input)
    save_message(chat_id, "agent", agent_reply)

    # Step 5: Return response
    return {"response": agent_reply}


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
