import os
import poe
import secrets
from typing import Annotated
from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

security = HTTPBasic()


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = os.getenv("UNAME").encode('utf-8')
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = os.getenv("PWORD").encode('utf-8')
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

class Body(BaseModel):
    prompt: str

@app.post("/")
def claude(username: Annotated[str, Depends(get_current_username)], body:Body):
    token = os.getenv("POE")
    client = poe.Client(token)
    prompt = body.prompt
    for chunk in client.send_message("a2", prompt):
        pass
    return chunk["text"]