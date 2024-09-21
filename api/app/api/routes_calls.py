import os
from shutil import copyfileobj
from fastapi import APIRouter, HTTPException, Header, Response, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from .jwt.jwt import verify_jwt_token
from api.app.repository import Repository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .utils import add_task_transcribe_async, transcribe_audio_async, get_task_status_async, Models
from api.app.database.consts import SECRET_KEY


router_calls = APIRouter(prefix="/calls", tags=["Звонки"])

calls_support_scheduler = AsyncIOScheduler(timezone="UTC")

@router_calls.post("/add_call_info")
async def call_info_add(info: str, phone_number: str, date_time: int, contact_name: str, length_seconds: int, call_type: int, file: UploadFile | None = None, record_id: str | None = None, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    filename = "no file"
    if file is not None:
        try:
            filename = file.filename
            await file.seek(0)
            with open(rf"/shared/calls/{file.filename}", "wb") as buffer:
                copyfileobj(file.file, buffer)
        except IOError as e:
            raise HTTPException(status_code=401, detail="file format error")
    ret_val = await Repository.add_call_record_to_storage(user_id=user.id, file=file, new_filename=filename, date_time=date_time, info=info, phone_number=phone_number, length_seconds=length_seconds, call_type=call_type, contact_name=contact_name, record_id=record_id)
    if not ret_val:
        raise HTTPException(status_code=400, detail="addition error")
    return ret_val


@router_calls.get("/get_all_calls")
async def get_all_calls(user_id: str, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    ret_val = await Repository.get_all_info_user_calls(user_id=user_id)
    return ret_val


@router_calls.get("/get_all_records_info")
async def get_all_records_info(user_id: str, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    ret_val = await Repository.get_all_user_call_records(user_id=user_id)
    return ret_val


@router_calls.get("/get_call_record_file")
async def get_call_record_file(user_id: str, record_id: str, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    file_info = await Repository.get_call_record(user_id=user.id, record_id=record_id)
    file_path = rf"/shared/calls/{file_info.name}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='application/octet-stream', filename=file_info.name)


@router_calls.get("/order_call_transcription")
async def order_call_transcription(user_id: str, record_id: str, model: str = Models.base, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    filename = await Repository.get_filename(user_id, record_id)
    return await add_task_transcribe_async(filename, user_id, record_id, model)


@router_calls.get("/get_order_transcription_status")
async def order_call_transcription(task_id: str, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    return await get_task_status_async(task_id)


@router_calls.put("/update_transcription")
async def update_transcription(transcription: str, user_id: str, record_id: str, secret_key: str | None = Header(default=None)):
    if not secret_key or secret_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await Repository.update_transcription(user_id=user_id, record_id=record_id, transcription=transcription)
