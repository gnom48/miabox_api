from fastapi import APIRouter, HTTPException, Header, Request
from .models import User, Statistics
from api.app.repository import *
from datetime import datetime
from .jwt import create_jwt_token, verify_jwt_token


router_users = APIRouter(prefix="/user", tags=["Пользователи"])


@router_users.get("/config")
async def get_config():
    return { "route": "user" }


# TODO: вернуть User
@router_users.post("/registration", status_code=201)
async def user_registration(user: UserTmp):
    res = await Repository.registrate_user(user)
    if not res:
        raise HTTPException(status_code=400, detail="registration error")
    return res


@router_users.get("/authorization", status_code=200)
async def user_authorization(login: str, password: str):
    current_user = await Repository.get_user_by_login(login, password)
    if current_user:
        return create_jwt_token(current_user)
    else:
        raise HTTPException(status_code=400, detail="authorization error")
    
    
@router_users.get("/info", status_code=200)
async def user_authorization(req: Request, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    return await verify_jwt_token(token_authorization)


# TODO: вернуть User
@router_users.put("/edit",status_code=200)
async def user_edit(user: UserTmp, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    cur_user = await verify_jwt_token(token_authorization)
    if user.id != cur_user.id:
        raise HTTPException(status_code=400, detail="uncorrect header")
    res = await Repository.edit_user(user)
    if not res:
        raise HTTPException(status_code=400, detail="edit error")
    return res


@router_users.post("/set_image", status_code=200)
async def set_image_to_user(image: Image, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    cur_user = await verify_jwt_token(token_authorization)
    return await Repository.edit_image(image, cur_user.id)


@router_users.get("/get_image", status_code=200)
async def set_image_to_user(token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    cur_user = await verify_jwt_token(token_authorization)
    return await Repository.get_image(cur_user.id)


@router_users.get("/teames")
async def user_teames(token_authorization: str | None = Header(default=None)):
    ...


@router_users.get("/config", status_code=200)
async def server_config_get():
    return { "postgres" : await Repository.get_config(), "api_datetime" : datetime.now() }