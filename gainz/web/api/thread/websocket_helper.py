from typing import Any

import openai
from fastapi import WebSocket
from typing_extensions import override

from gainz.settings import settings

from .schema import convert_message

client = openai.AsyncOpenAI(api_key=settings.openai_key)
assistant_id_cache = None
BOT_NAME = "Messi"
BOT_MODEL = "gpt-3.5-turbo"
BOT_INSTRUCTION = "You are a sport coach."
REPLY_INSTRUCTION = "Please address the user as Champ."
OpenAIMessage = openai.types.beta.threads.message.Message


class ConnectionManager(openai.AsyncAssistantEventHandler):
    """Event Handler for websocket and OpenAI's stream."""

    def __init__(self) -> None:
        self.active_threads: dict[str, list[WebSocket]] = {}

    async def connect(self, thread_id: str, websocket: WebSocket) -> None:
        """Register websocket connection."""

        await websocket.accept()
        self.active_threads[thread_id].append(websocket)

    def disconnect(self, thread_id: str, websocket: WebSocket) -> None:
        """Unregister websocket connection."""
        self.active_threads[thread_id].remove(websocket)

    async def broadcast(self, message: OpenAIMessage) -> None:
        """Broadcast message back to all clients."""
        payload = convert_message(message)
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


class _SingletonAssistant:
    id: str = ""

    async def get_id(self) -> str:
        """Lazy initialization of assistant."""

        if self.id == "":
            assistants = await client.beta.assistants.list()
            if len(assistants.data) == 0:
                assistant = await client.beta.assistants.create(
                    tools=[],
                    name=BOT_NAME,
                    model=BOT_MODEL,
                    instructions=BOT_INSTRUCTION,
                )
                self.id = assistant.id
            else:
                self.id = assistants.data[0].id
        return self.id


assistant = _SingletonAssistant()


async def bot_reply(thread_id: str, manager: ConnectionManager) -> None:
    """Initiate a bot reply."""
    assistant_id = await assistant.get_id()
    client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=REPLY_INSTRUCTION,
        event_handler=manager,
    )
