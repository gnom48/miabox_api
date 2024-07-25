import asyncio
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from .consts import SECRET_KEY
from .trascription import AsyncWhisper, Models
from .utils import put_transcribe_result_async
from typing import Any, Dict
from .states import TaskStatus


async_whisper: AsyncWhisper = AsyncWhisper()
router_transcription = APIRouter(prefix="/transcription", tags=["Транскрипция"])

task_queue = asyncio.Queue()
task_status: Dict[str, Any] = {}


async def task_handler():
    while True:
        task_id, file, user_id, record_id, model = await task_queue.get() # тут вроде бы встроенное ожидание, не надо ничего городить
        task_status[task_id]["status"] = TaskStatus.proccessing

        try:
            transcription = await async_whisper.transcribe_async(file)
            res = await put_transcribe_result_async(transcription=transcription, user_id=user_id, record_id=record_id)
            task_status[task_id]["status"] = TaskStatus.completed
            task_status[task_id]["result"] = transcription["text"] # потом при анализе можно отдавать весь результат
            if not res:
                raise Exception("error uploading to main api")
        except Exception as e:
            task_status[task_id]["status"] = TaskStatus.failed
            task_status[task_id]["error"] = str(e)

        task_queue.task_done()


@router_transcription.get("/config")
async def get_config():
    return { "route": "transcription" }


@router_transcription.get("/get_transcription")
async def get_transcription(file: str, user_id: int, record_id: int, model: str = Models.base, secret_key: str | None = Header(default=None)):
    if not secret_key or secret_key != SECRET_KEY:
        raise HTTPException(status_code=400, detail="uncorrect header")
    if file == "" or file is None:
        raise HTTPException(status_code=404, detail="no file to transcribe")
    if async_whisper.model_name != model:
        await async_whisper.initialize_async(model)
    res = await async_whisper.transcribe_async(file_name=file)
    return { "result": res, "details": "Warning! Endpoint is depricated."}


@router_transcription.get("/add_task_transcription")
async def add_task_transcription(file: str, user_id: int, record_id: int, model: str = Models.base, secret_key: str | None = Header(default=None)):
    if not secret_key or secret_key != SECRET_KEY:
        raise HTTPException(status_code=400, detail="uncorrect header")
    if file == "" or file is None:
        raise HTTPException(status_code=404, detail="no file to transcribe")
    if async_whisper.model_name != model:
        await async_whisper.initialize_async(model)
    task_id = f"task_{len(task_status) + 1}"
    task_status[task_id] = {"status": TaskStatus.queued, "file": file, "model": model}
    await task_queue.put((task_id, file, user_id, record_id, model))
    return JSONResponse(content={"task_id": task_id, "status": TaskStatus.queued})


@router_transcription.get("/get_task_status")
async def get_task_status(task_id: str, secret_key: str | None = Header(default=None)):
    if not secret_key or secret_key != SECRET_KEY:
        raise HTTPException(status_code=400, detail="uncorrect header")
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content=task_status[task_id])