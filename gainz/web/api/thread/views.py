import logging

from fastapi import APIRouter

from gainz.services.openai import client

from .schema import Message, Thread, convert_message, convert_thread

router = APIRouter()
all_threads: dict[str, Thread] = {}


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
        logging.error(e, exc_info=True)
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
        logging.error(e, exc_info=True)
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
        logging.error(e, exc_info=True)
        raise e
