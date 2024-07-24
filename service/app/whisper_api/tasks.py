from celery import Celery
from .routes_transcription import async_whisper


app = Celery("tasks", broker="redis://redis:6379/0")


# @app.task
# async def transcribe_task(file_name, model):
#     if async_whisper.model_name != model:
#         await async_whisper.initialize_async(model)
#     return await async_whisper.transcribe_async(file_name)

@app.task
def transcribe_task(file_name, model):
    if async_whisper.model_name != model:
        async_whisper.initialize_sync(model)
    return async_whisper.transcribe_sync(file_name)
