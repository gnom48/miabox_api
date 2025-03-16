from fastapi import APIRouter, Depends, HTTPException, Header, status
from app.database import UserStatusesOrm, UserTeamOrm
from app.api import AddresInfo, UserCredentials, get_user_from_request
from app.database import Repository

router_addresses = APIRouter(prefix="/address", tags=["Адреса"])


@router_addresses.post("/add_address_info")
async def address_info_add(address_info: AddresInfo, user_credentials: UserCredentials = Depends(get_user_from_request)):
    ret_val = await Repository.add_address_info(data=address_info)
    if not ret_val:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="addition error")
    return ret_val


@router_addresses.get("/get_address_info_by_user_id")
async def get_address_info_by_user_id(user_id: str, date_start: int | None = None, date_end: int | None = None, user_credentials: UserCredentials = Depends(get_user_from_request)):
    return await Repository.get_address_info_by_user_id(user_id=user_id, date_start=date_start, date_end=date_end)
