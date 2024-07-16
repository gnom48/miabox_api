import io
from fastapi import APIRouter, HTTPException, Header, Response, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from app.api.jwt.jwt import verify_jwt_token
from app.database.models import UserStatusesOrm, UserTeamOrm
from app.api.models import AddresInfo
from app.repository import Repository
import time


router_calls = APIRouter(prefix="/calls", tags=["Звонки"])


@router_calls.post("/add_call_info")
async def call_info_add(file: UploadFile, info: str, phone_number: str, date_time: int, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    ret_val = await Repository.add_call_record_to_storage(user_id=user.id, file=file, date_time=date_time, info=info, phone_number=phone_number)
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
