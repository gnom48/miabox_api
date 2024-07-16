from fastapi import FastAPI
from service.whisper_api import router_transcription, async_whisper, Models
from contextlib import asynccontextmanager


# uvicorn service.main:app --reload --host localhost --port 8000


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Старт")
    await async_whisper.initialize_async(Models.base)
    print("Модель по умолчанию готова")
    yield
    print("Выключение")


app = FastAPI(lifespan=lifespan)
app.include_router(router_transcription)
