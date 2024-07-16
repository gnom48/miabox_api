import asyncio
import whisper


class Models:
    tiny = "tiny"
    base = "base"
    small = "small"
    medium = "medium"
    large = "large"


class AsyncWhisper:
    def __init__(self):
        self.model_name = Models.base
        self.model = None

    async def initialize_async(self, model_name: str = Models.base):
        self.model_name = model_name
        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(None, whisper.load_model, self.model_name)

    async def transcribe_async(self, file_name):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.model.transcribe, file_name)
        return result
