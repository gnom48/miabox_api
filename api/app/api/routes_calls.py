from shutil import copyfileobj
from fastapi import APIRouter, HTTPException, Header, Response, UploadFile
from .jwt.jwt import verify_jwt_token
from api.app.repository import Repository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .utils import transcribe_audio_async
import time


router_calls = APIRouter(prefix="/calls", tags=["Звонки"])

calls_support_scheduler = AsyncIOScheduler(timezone="UTC")

@router_calls.post("/add_call_info")
async def call_info_add(file: UploadFile, info: str, phone_number: str, date_time: int, contact_name: str, length_seconds: int, call_type: int, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    try:
        with open("/shared/calls/" + f"{user.id}_" + file.filename, "wb") as buffer:
            copyfileobj(file.file, buffer)
        print(f"Принят файл: {file.filename} - {file.size} | {file.content_type}")
    except IOError as e:
        raise HTTPException(status_code=501, detail="file format error")
    ret_val = await Repository.add_call_record_to_storage(user_id=user.id, file=file, date_time=date_time, info=info, phone_number=phone_number, length_seconds=length_seconds, call_type=call_type, contact_name=contact_name)
    if not ret_val:
        raise HTTPException(status_code=400, detail="addition error")
    return ret_val


@router_calls.get("/get_all_calls")
async def get_all_calls(user_id: int, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    ret_val = await Repository.get_all_info_user_calls(user_id=user_id)
    return ret_val


@router_calls.get("/get_call_record_file")
async def get_call_record_filestream(user_id: int, record_id: int, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    file_data = await Repository.get_call_record_from_storage(user_id=user.id, record_id=record_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")
    return Response(file_data, media_type="application/octet-stream")


@router_calls.get("/order_call_transcription")
async def order_call_transcription(user_id: int, record_id: int, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    job = calls_support_scheduler.add_job(func=transcribe_audio_async, trigger="interval", seconds=3)
    calls_support_scheduler.start()
    return { "transcription_task": job.id, "date_time": int(time.time()), "position": 0}


@router_calls.put("/update_transcription")
async def update_transcription(transcription: str, user_id: int, record_id: int, secret_key: str | None = Header(default=None)):
    if not secret_key or secret_key != "miabox": # TODO: вынести в константу
        raise HTTPException(status_code=400, detail="uncorrect header")
    return await Repository.update_transcription(user_id=user_id, record_id=record_id, transcription=transcription)