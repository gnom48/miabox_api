import os
import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Response, UploadFile, status
from app.api import User, AuthData, RegData, UserCredentials
from app.database import *
from datetime import datetime
from shutil import copyfileobj
from fastapi.responses import FileResponse
from app.api import get_user_from_request, UserCredentials
from app.toml_helper import load_var_from_toml


router_users = APIRouter(prefix="/user", tags=["Пользователи"])


@router_users.get("/info", status_code=status.HTTP_200_OK)
async def user_authorization(user_credentials: UserCredentials = Depends(get_user_from_request)):
    return user_credentials

# TODO: edit -> update


@router_users.put("/edit", status_code=status.HTTP_200_OK)
async def user_edit(user: User, user_credentials: UserCredentials = Depends(get_user_from_request)):
    if user.id != user_credentials.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    res = await Repository.edit_user(user)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="edit error")
    return res

# TODO: set_image_file -> set_avatar


@router_users.post("/set_image_file", status_code=status.HTTP_200_OK)
async def set_image_to_user_by_file(file: UploadFile, user_credentials: UserCredentials = Depends(get_user_from_request)):
    try:
        await file.seek(0)
        with open(rf"/shared/images/{file.filename}", "wb") as buffer:
            copyfileobj(file.file, buffer)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="file operation error")
    res = await Repository.edit_image_file(file, file.filename, user_credentials.id)
    if res is not None:
        return res
    raise HTTPException(
        status_code=status.HTTP_status.HTTP_402_PAYMENT_REQUIRED_PAYMENT_REQUIRED, detail="db operation error")

# TODO: get_image_file -> get_avatar


@router_users.get("/get_image_file", status_code=status.HTTP_200_OK)
async def set_image_to_user(user_id: str, user_credentials: UserCredentials = Depends(get_user_from_request)):
    image = await Repository.get_image(user_id)
    file_path = rf"/shared/images/{image.name}"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return FileResponse(file_path, media_type='application/octet-stream', filename=image.name)
