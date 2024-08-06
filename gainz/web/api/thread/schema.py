from typing import Any

from pydantic import BaseModel


class Thread(BaseModel):
    """less-verbose version of Thread."""

    id: str
    created_at: int


class Message(BaseModel):
    """less-verbose version of Message."""

    id: str
    assistant_id: str
    user_id: str
    created_at: int
    text: str
    replace: bool = False


def convert_thread(raw_response: Any) -> Thread:
    """Conversion utility."""

    return Thread(id=raw_response.id, created_at=raw_response.created_at)


def convert_message(raw_response: Any) -> Message:
    """Conversion utility."""

    user_id = raw_response.metadata.get("user_id", "")
    text = raw_response.content[0].text.value if len(raw_response.content) > 0 else ""
    assistant_id = raw_response.assistant_id if raw_response.assistant_id is str else ""
    return Message(
        id=raw_response.id,
        created_at=raw_response.created_at,
        assistant_id=assistant_id,
        user_id=user_id,
        text=text,
    )
