from fastapi import APIRouter, HTTPException, Header
from .consts import SECRET_KEY
from .trascription import AsyncWhisper, Models
from celery.result import AsyncResult
from celery import Celery


async_whisper: AsyncWhisper = AsyncWhisper()
router_transcription = APIRouter(prefix="/transcription", tags=["Транскрипция"])

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


@router_transcription.get("/get_transcription")
async def get_transcription(file: str, model: str = "base", secret_key: str | None = Header(default=None)):
    if not secret_key or secret_key != SECRET_KEY:
        raise HTTPException(status_code=400, detail="uncorrect header")
    if file == "" or file is None:
        raise HTTPException(status_code=404, detail="no file to transcribe")
    if async_whisper.model_name != model:
        await async_whisper.initialize_async(model)
    return await async_whisper.transcribe_async(file_name=file)


@router_transcription.get("/add_task_transcription")
async def add_task_transcription(file: str, model: str = "base", secret_key: str | None = Header(default=None)):
    if not secret_key or secret_key != SECRET_KEY:
        raise HTTPException(status_code=400, detail="uncorrect header")
    if file == "" or file is None:
        raise HTTPException(status_code=404, detail="no file to transcribe")
    task = transcribe_task.apply_async((file, model))
    return {"task_id": str(task.id)}


@router_transcription.get("/get_transcription_result/{task_id}")
async def get_transcription_result(task_id: str, secret_key: str | None = Header(default=None)):
    if not secret_key or secret_key != SECRET_KEY:
        raise HTTPException(status_code=400, detail="uncorrect header")
    task = AsyncResult(task_id, app=transcribe_task.app)
    if task.state == "PENDING":
        response = {"state": task.state, "status": "Task is pending..."}
    elif task.state != "FAILURE":
        response = {"state": task.state, "result": task.result}
        if "result" in response:
            response["status"] = "Task completed successfully"
        else:
            response["status"] = "Task is running..."
    else:
        response = {"state": task.state, "status": str(task.info), "result": None}
    return response
