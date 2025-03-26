from fastapi import APIRouter, Depends, HTTPException, Header, Request, Response, UploadFile, status
from fastapi.responses import RedirectResponse
from app.api.models import User, UserCredentials
from app.database import BaseRepository, UsersRepository, FilesRepository
from app.api.middlewares import get_user_from_request
from app.utils.minio_client import MinioClient


router_users = APIRouter(prefix="/user", tags=["Пользователи"])

# GOOD: полностью исправно
# GOOD: соответствует потребностям приложения


@router_users.get("/info", status_code=status.HTTP_200_OK)
async def user_authorization(
    user_credentials: UserCredentials = Depends(get_user_from_request),
    user_repository: UsersRepository = Depends(
        UsersRepository.repository_factory)
):
    async with user_repository:
        return await user_repository.get_user_by_id(user_credentials.id)


@router_users.put("/update", status_code=status.HTTP_200_OK)
async def update_user(
    user: User,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    user_repository: UsersRepository = Depends(
        UsersRepository.repository_factory)
):
    if user.id != user_credentials.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not self account")
    async with user_repository:
        res = await user_repository.update_user(user)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="update error")
        return res


@router_users.post("/set_avatar", status_code=status.HTTP_200_OK)
async def set_avatar(
    file: UploadFile,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    user_repository: UsersRepository = Depends(
        UsersRepository.repository_factory),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory),
    minio_client: MinioClient = Depends(MinioClient.minio_client_factory)
):
    async with files_repository:
        minio_client.upload_file(user_credentials.id, file)
        new_avatar_file_id = await files_repository.add_file(file.filename, user_credentials.id, user_credentials.id)
        async with user_repository:
            if await user_repository.update_avatar_only(user_credentials.id, new_avatar_file_id):
                return new_avatar_file_id
            return None
