from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Header, UploadFile, status
from fastapi.responses import FileResponse
from app.database.repositories import CallsRepository, FilesRepository
from app.api.models import UserCredentials, Call
from app.api.middlewares import get_user_from_request
from app.utils.minio_client import MinioClient
from app.utils import rabbitmq

router_calls = APIRouter(prefix="/calls", tags=["Звонки"])


@router_calls.post("/", status_code=status.HTTP_201_CREATED, description="Добавляет новую запись о совершённом текущим пользователем звонке; можно добавить аудиозапись звонка")
async def add_call(
    file: Optional[UploadFile] = None,
    date_time: int = Form(...),
    phone_number: str = Form(...),
    contact_name: str = Form(...),
    length_seconds: int = Form(...),
    call_type: int = Form(...),
    user_credentials: UserCredentials = Depends(get_user_from_request),
    calls_repository: CallsRepository = Depends(
        CallsRepository.repository_factory),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory),
    minio_client: MinioClient = Depends(MinioClient.minio_client_factory)
):
    call = Call(
        id="",
        user_id=user_credentials.id,
        date_time=date_time,
        phone_number=phone_number,
        contact_name=contact_name,
        length_seconds=length_seconds,
        call_type=call_type,
        transcription=None,
        file_id=None
    )
    new_file_id: str | None = None
    if file is not None:
        try:
            await file.seek(0)
            minio_client.upload_file(user_credentials.id, file)
            new_file_id = await files_repository.add_file(file.filename, user_credentials.id, user_credentials.id)
        except IOError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File format error")

    async with calls_repository:
        call.file_id = new_file_id
        record_id = await calls_repository.add_call_record_to_storage(call)
        if not record_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to add call record")
        return record_id


@router_calls.get("/user/{user_id}", status_code=status.HTTP_200_OK, description="Возвращает все звонки пользователя по его Id")
async def get_calls(
    user_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    calls_repository: CallsRepository = Depends(
        CallsRepository.repository_factory)
):
    # TODO: проверка доступа
    async with calls_repository:
        calls = await calls_repository.get_all_info_user_calls(user_id)
        if calls is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Calls not found")
        return calls


@router_calls.get("/{call_id}/transcription", status_code=status.HTTP_200_OK, description="Запускает расшифровку аудиозаписи звонка по его Id, если она была прикреплена (работать не будет, нейронка не поднята)")
async def order_call_transcription(
    call_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    calls_repository: CallsRepository = Depends(
        CallsRepository.repository_factory),
    files_repository: FilesRepository = Depends(
        FilesRepository.repository_factory)
):
    # TODO: проверка доступа
    async with calls_repository:
        async with files_repository:
            call = await calls_repository.get_one_call(call_id)
            file_id = call.file_id
            if not file_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="File info not found")
            file_info = await files_repository.get_file_info_by_id(file_id)
            if not file_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
            return await rabbitmq.send_message_to_queue(call_id=call_id, object_name=file_info.obj_name, bucket_name=file_info.bucket_name)


# BAD: выискивать сообщение в очередях бессмысленно
# @router_calls.get("/transcription/{call_id}/status", status_code=status.HTTP_200_OK)
# async def get_order_transcription_status(
#     call_id: str,
#     user_credentials: UserCredentials = Depends(get_user_from_request),
#     calls_repository: CallsRepository = Depends(
#         CallsRepository.repository_factory)
# ):
#     return "In proccess"


@router_calls.put("/transcription", status_code=status.HTTP_200_OK, description="Обновляет расшифровку звонка")
async def update_transcription(
    transcription: str,
    call_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    calls_repository: CallsRepository = Depends(
        CallsRepository.repository_factory)
):
    async with calls_repository:
        success = await calls_repository.update_transcription(call_id, transcription)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Unable to update transcription")
        return {"detail": "Transcription updated successfully"}
