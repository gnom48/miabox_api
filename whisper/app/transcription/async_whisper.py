import asyncio
import whisper


class Models:
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class AsyncWhisper:
    def __init__(self):
        self.model_name = Models.BASE
        self.model = None

    async def initialize_async(self, model_name: str = Models.BASE):
        self.model_name = model_name
        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(None, whisper.load_model, self.model_name)

    def initialize_sync(self, model_name: str = Models.BASE):
        self.model_name = model_name
        self.model = whisper.load_model(self.model_name)

    async def transcribe_async(self, file_path) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.model.transcribe, file_path)

    def transcribe_sync(self, file_path) -> str:
        return self.model.transcribe(file_path)
