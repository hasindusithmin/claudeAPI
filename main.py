import os
import poe
from enum import Enum
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="claudeAPI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
security = HTTPBasic()

def check_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    if username == os.getenv('UNAME') and password == os.getenv('PWORD'):
        return username
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

class Body(BaseModel):
    prompt: str

class ChatBot(str, Enum):
    capybara ="sage"
    a2 ="claude"
    chinchilla="chatgpt"
    llama_2_7b_chat = 'Llama'

@app.get("/")
def root():
    return {"message":"keep alive"}

@app.post("/")
async def reply(body:Body,user: str = Depends(check_user),engine:ChatBot = None):
    try:
        engine = "a2" if engine is None else engine.name
        token = os.getenv("POE")
        print(f'🔖🔖 {token[:10]}...')
        client = poe.Client(token)
        prompt = body.prompt
        for chunk in client.send_message(engine, prompt):
            pass
        return chunk["text"]
    except:
        raise HTTPException(status_code=500,detail="Please try again later")