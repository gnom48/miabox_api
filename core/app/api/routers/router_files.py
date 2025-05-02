from typing import Optional
from fastapi import APIRouter, Depends, Form, UploadFile, status, HTTPException
from fastapi.responses import FileResponse
from app.database.repositories import FilesRepository
from app.api.models import UserCredentials, FileAccessMode
from app.api.middlewares import get_user_from_request
from app.utils.minio_client import MinioClient


router_files = APIRouter(prefix="/files", tags=["Файлы"])


@router_files.get("/{file_id}", status_code=status.HTTP_200_OK)
async def get_file_info(
    file_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory)
):
    async with files_repository:
        return await files_repository.get_file_info_by_id(file_id)


@router_files.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    file_id: Optional[str] = Form(...),
    user_credentials: UserCredentials = Depends(get_user_from_request),
    minio_client: MinioClient = Depends(MinioClient.minio_client_factory),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory)
):
    async with files_repository:
        res = minio_client.upload_file(user_credentials.id, file)
        return await files_repository.add_file(file.filename, user_credentials.id, user_credentials.id, file_id)


@router_files.get("/{file_id}/download", status_code=status.HTTP_200_OK)
async def download_file_stream(
    file_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    minio_client: MinioClient = Depends(MinioClient.minio_client_factory),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory)
):
    # REVIEW: возвращает реально поток, без имени файла, мб перевернутый и тд
    async with files_repository:
        # if not await files_repository.check_access(FileAccessMode.READ, user_credentials.id, file_id):
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        file_info = await files_repository.get_file_info_by_id(file_id)
        return minio_client.download_file(file_info.bucket_name, file_info.obj_name)


@router_files.get("/{file_id}/presigned_url", status_code=status.HTTP_200_OK)
async def get_presigned_file(
    file_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    minio_client: MinioClient = Depends(MinioClient.minio_client_factory),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory)
):
    async with files_repository:
        # if not await files_repository.check_access(FileAccessMode.READ, user_credentials.id, file_id):
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        file_info = await files_repository.get_file_info_by_id(file_id)
        if user_credentials.id in list(map(lambda item: item.user_id, await files_repository.get_file_access(file_id))):
            url = minio_client.get_presigned_url(
                file_info.bucket_name, file_info.obj_name)
            return {"url": url}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router_files.delete("/{file_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_file(
    file_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    minio_client: MinioClient = Depends(MinioClient.minio_client_factory),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory)
):
    async with files_repository:
        # if not await files_repository.check_access(FileAccessMode.READ, user_credentials.id, file_id):
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        file_info = await files_repository.get_file_info_by_id(file_id)
        delete_success = await files_repository.delete_file(file_id)
        if not delete_success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return minio_client.delete_file(file_info.bucket_name, file_info.obj_name)
