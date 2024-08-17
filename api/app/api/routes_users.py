import os
from fastapi import APIRouter, HTTPException, Header, Request, Response, UploadFile
from .models import User, Statistics
from api.app.repository import *
from datetime import datetime
from .jwt import create_jwt_token, verify_jwt_token
from shutil import copyfileobj
from fastapi.responses import FileResponse


router_users = APIRouter(prefix="/user", tags=["Пользователи"])


@router_users.get("/config", status_code=200)
async def server_config_get():
    return { "postgres" : await Repository.get_config(), "api_datetime" : datetime.now() }


@router_users.post("/registration", status_code=201)
async def user_registration(user: User):
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
        raise HTTPException(status_code=401, detail="authorization error")


@router_users.post("/authorization_secure", status_code=200)
async def authorization_secure(auth_data: AuthData):
    current_user = await Repository.get_user_by_login(auth_data.login, auth_data.password)
    if current_user:
        return create_jwt_token(current_user)
    else:
        raise HTTPException(status_code=401, detail="authorization error")
    
    
@router_users.get("/info", status_code=200)
async def user_authorization(req: Request, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await verify_jwt_token(token_authorization)


@router_users.put("/edit",status_code=200)
async def user_edit(user: User, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    cur_user = await verify_jwt_token(token_authorization)
    if user.id != cur_user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = await Repository.edit_user(user)
    if not res:
        raise HTTPException(status_code=400, detail="edit error")
    return res


@router_users.post("/set_image_file", status_code=200)
async def set_image_to_user_by_file(file: UploadFile, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    try:
        await file.seek(0)
        with open(rf"/shared/images/{file.filename}", "wb") as buffer:
            copyfileobj(file.file, buffer)
    except IOError as e:
        raise HTTPException(status_code=401, detail="file operation error")
    res = await Repository.edit_image_file(file, f"{file.filename}", user.id)
    if res is not None:
        return res
    raise HTTPException(status_code=402, detail="db operation error")


@router_users.get("/get_image_file", status_code=200)
async def set_image_to_user(token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    cur_user = await verify_jwt_token(token_authorization)
    image = await Repository.get_image(cur_user.id)
    file_path = rf"/shared/images/{image.name}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path, media_type='application/octet-stream', filename=image.name)
