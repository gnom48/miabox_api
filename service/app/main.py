import asyncio
from fastapi import FastAPI
from .whisper_api import router_transcription, async_whisper, Models, task_handler
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Старт")
    await async_whisper.initialize_async(Models.base)
    print("Модель по умолчанию готова")
    asyncio.create_task(task_handler())
    yield
    print("Выключение")


app = FastAPI(lifespan=lifespan)
app.include_router(router_transcription)
