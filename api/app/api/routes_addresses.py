from fastapi import APIRouter, HTTPException, Header
from .jwt.jwt import verify_jwt_token
from api.app.database.models import UserStatusesOrm, UserTeamOrm
from .models import AddresInfo
from api.app.repository import Repository


router_addresses = APIRouter(prefix="/address", tags=["Адреса"])


@router_addresses.post("/add_address_info")
async def address_info_add(address_info: AddresInfo, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    ret_val = await Repository.add_address_info(data=address_info)
    if not ret_val:
        raise HTTPException(status_code=400, detail="addition error")
    return ret_val


@router_addresses.get("/get_address_info_by_user_id")
async def get_address_info_by_user_id(user_id: int, date_start: int | None = None, date_end: int | None = None, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    ret_val = await Repository.get_address_info_by_user_id(user_id=user_id, date_start=date_start, date_end=date_end)
    return ret_val


@router_addresses.get("/get_address_info_by_team")
async def get_address_info_by_team(token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    raise HTTPException(status_code=400, detail="Depricated!")