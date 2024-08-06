import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from gainz.services.jwt_auth import decode_user_data

from .schema import Message, Thread, convert_message, convert_thread
from .websocket_helper import ConnectionManager, bot_reply, client

router = APIRouter()
all_threads: dict[str, Thread] = {}
manager = ConnectionManager()


@router.get("/threads")
async def list_threads() -> list[Thread]:
    """List threads in this session, persistence is beyond the project's scope."""

    # listing is missing from API for security reason
    # ref: https://community.openai.com
    # /t/list-of-threads-is-missing-from-the-api/484510
    return list(all_threads.values())


@router.post("/threads")
async def create_thread() -> Thread:
    """Create a thread."""

    try:
        new_thread = await client.beta.threads.create()
        retval = convert_thread(new_thread)
        all_threads[retval.id] = retval
        return retval
    except Exception as e:
        logging.critical(e, exc_info=True)
        raise e


@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str) -> str:
    """Delete a thread."""

    try:
        await client.beta.threads.delete(thread_id)
        if thread_id in all_threads:
            del all_threads[thread_id]
        return "success"
    except Exception as e:
        logging.critical(e, exc_info=True)
        raise e


@router.get("/threads/{thread_id}/messages")
async def list_messages(thread_id: str, after: str = "") -> list[Message]:
    """List messages in a thread."""
    try:
        if after != "":
            messages = await client.beta.threads.messages.list(
                thread_id,
                limit=100,
                after=after,
            )
        else:
            messages = await client.beta.threads.messages.list(
                thread_id,
                limit=100,
            )
        return list(map(convert_message, messages.data))
    except Exception as e:
        logging.critical(e, exc_info=True)
        raise e


@router.websocket("/ws/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str, token: str) -> None:
    """Send and receive messages to a thread."""

    user_data = decode_user_data(token)
    await manager.connect(thread_id, websocket)

    try:
        while True:
            content = await websocket.receive_text()
            user_message = await client.beta.threads.messages.create(
                thread_id,
                role="user",
                content=content,
                metadata={"user_id": user_data.user_id},
            )
            await manager.broadcast(user_message)
            await bot_reply(thread_id, manager)
    except WebSocketDisconnect:
        manager.disconnect(thread_id, websocket)
