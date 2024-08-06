from typing import Annotated, Dict

import jwt
from fastapi import Header, HTTPException
from pydantic import BaseModel

from gainz.settings import settings

SECRET: str = settings.auth_jwt_secret
ALGORITHM: str = "HS256"
USERS: Dict[str, str] = {"api_key_1": "user_1", "api_key_2": "user_2"}


class UserData(BaseModel):
    """User data residing in JWT."""

    user_id: str


def encode_user_data(api_key: str) -> str:
    """Encode user data from the given api_key."""

    if USERS.get(api_key) is None:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    payload = {"user_id": USERS[api_key]}
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


async def decode_auth_header(x_token: Annotated[str, Header()]) -> UserData:
    """Decode user data from encrypted X-Token http header."""

    try:
        payload = jwt.decode(x_token, SECRET, algorithms=[ALGORITHM])
        if payload.get("user_id") is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UserData(user_id=payload["user_id"])
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e


def decode_user_data(token: str) -> UserData:
    """Decode user data from string, useful when http header is not present."""

    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        if payload.get("user_id") is None:
            raise Exception("Invalid token")
        return UserData(user_id=payload["user_id"])
    except jwt.ExpiredSignatureError as e:
        raise Exception("Token expired") from e
    except jwt.InvalidTokenError as e:
        raise Exception("Invalid token") from e
