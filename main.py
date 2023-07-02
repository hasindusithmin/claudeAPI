import os
import poe
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

@app.get("/")
def root():
    return {"message":"keep alive"}

@app.post("/")
async def reply(body:Body,user: str = Depends(check_user)):
    token = os.getenv("POE")
    client = poe.Client(token)
    prompt = body.prompt
    for chunk in client.send_message("a2", prompt):
        pass
    return chunk["text"]
