import openai

from gainz.settings import settings

client = openai.AsyncOpenAI(api_key=settings.openai_key)
assistant_id_cache = None
BOT_NAME = "Messi"
BOT_MODEL = "gpt-3.5-turbo"
BOT_INSTRUCTION = "You are a sport coach."
REPLY_INSTRUCTION = "Please address the user as Champ."


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
