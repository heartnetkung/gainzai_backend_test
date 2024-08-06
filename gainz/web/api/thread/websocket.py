from typing import Any

import openai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing_extensions import override

from gainz.services.jwt_auth import decode_user_data
from gainz.services.openai import REPLY_INSTRUCTION, assistant, client

from .schema import convert_message

OpenAIMessage = openai.types.beta.threads.message.Message


class ConnectionManager(openai.AsyncAssistantEventHandler):
    """Event Handler for websocket and OpenAI's stream."""

    def __init__(self) -> None:
        self.active_threads: dict[str, list[WebSocket]] = {}

    async def connect(self, thread_id: str, websocket: WebSocket) -> None:
        """Register websocket connection."""

        await websocket.accept()
        if thread_id not in self.active_threads:
            self.active_threads[thread_id] = []
        self.active_threads[thread_id].append(websocket)

    def disconnect(self, thread_id: str, websocket: WebSocket) -> None:
        """Unregister websocket connection."""
        self.active_threads[thread_id].remove(websocket)

    async def broadcast(self, message: OpenAIMessage) -> None:
        """Broadcast message back to all clients."""
        payload = convert_message(message).model_dump()
        for connection in self.active_threads[message.thread_id]:
            await connection.send_json(payload)

    @override
    async def on_message_created(self, message: OpenAIMessage) -> None:
        await self.broadcast(message)

    @override
    async def on_message_delta(self, delta: Any, snapshot: OpenAIMessage) -> None:
        await self.broadcast(snapshot)

    @override
    async def on_message_done(self, message: OpenAIMessage) -> None:
        await self.broadcast(message)


async def bot_reply(thread_id: str, manager: ConnectionManager) -> None:
    """Initiate a bot reply."""
    assistant_id = await assistant.get_id()
    client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=REPLY_INSTRUCTION,
        event_handler=manager,
    )


ws = FastAPI()
manager = ConnectionManager()


@ws.websocket("/threads/{thread_id}")
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
