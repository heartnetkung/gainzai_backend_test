from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from gainz.services.jwt_auth import UserData, decode_auth_header, encode_user_data

router = APIRouter()


@router.get("/current_user")
async def current_user(
    user_data: Annotated[UserData, Depends(decode_auth_header)],
) -> UserData:
    """Get the user_data represented in this JWT."""
    return user_data


class APIKey(BaseModel):
    """simple payload structure."""

    api_key: str


@router.post("/auth")
async def auth(payload: APIKey) -> str:
    """Authenticate and return jwt_token."""
    return encode_user_data(payload.api_key)
