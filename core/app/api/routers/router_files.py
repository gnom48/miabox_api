from fastapi import APIRouter, Depends, UploadFile, status, HTTPException
from fastapi.responses import FileResponse
from app.database.repositories import FilesRepository
from app.database.models import FileAccessModeOrm
from app.api.models import UserCredentials
from app.api.middlewares import get_user_from_request
from app.utils.minio_client import MinioClient


router_files = APIRouter(prefix="/files", tags=["Файлы"])


@router_files.get("/info", status_code=status.HTTP_200_OK)
async def get_file_info(
    file_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory)
):
    async with files_repository:
        return await files_repository.get_file_info_by_id(file_id)


@router_files.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    minio_client: MinioClient = Depends(MinioClient.minio_client_factory),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory)
):
    async with files_repository:
        minio_client.upload_file(user_credentials.id, file)
        return await files_repository.add_file(file.filename, user_credentials.id, user_credentials.id)


@router_files.get("/download", status_code=status.HTTP_200_OK)
async def download_file(
    file_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    minio_client: MinioClient = Depends(MinioClient.minio_client_factory),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory)
):
    async with files_repository:
        file_info = await files_repository.get_file_info_by_id(file_id)
        if user_credentials.id in list(map(lambda item: item.user_id, await files_repository.get_file_access(file_id))):
            # return minio_client.download_file(file_info.bucket_name, file_info.obj_name)
            return FileResponse(minio_client.download_file(
                file_info.bucket_name, file_info.obj_name), media_type='application/octet-stream', filename=file_info.obj_name)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router_files.get("/presigned_url", status_code=status.HTTP_200_OK)
async def pre_signed_file(
    file_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    minio_client: MinioClient = Depends(MinioClient.minio_client_factory),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory)
):
    async with files_repository:
        file_info = await files_repository.get_file_info_by_id(file_id)
        if user_credentials.id in list(map(lambda item: item.user_id, await files_repository.get_file_access(file_id))):
            url = minio_client.get_presigned_url(
                file_info.bucket_name, file_info.obj_name)
            return {"url": url}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router_files.delete("/delete", status_code=status.HTTP_202_ACCEPTED)
async def delete_file(
    file_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    minio_client: MinioClient = Depends(MinioClient.minio_client_factory),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory)
):
    async with files_repository:
        file_info = await files_repository.get_file_info_by_id(file_id)
        file_access_list = await files_repository.get_file_access(file_id)
        if any(item.user_id == user_credentials.id and item.file_access_mode == FileAccessModeOrm.WRITE for item in file_access_list):
            await files_repository.delete_file(file_id)
            return minio_client.delete_file(file_info.bucket_name, file_info.obj_name)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
