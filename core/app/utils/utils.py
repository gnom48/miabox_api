import aiohttp
from core.app.database.consts import WHISPER_API_URL, SECRET_KEY
from core.app.database.repository import Repository
from warnings import deprecated

# TODO: модель не должна задаваться отсюда
# как сервис сконфигурирован так он и работает сам по себе


class Models:
    tiny = "tiny"
    base = "base"
    small = "small"
    medium = "medium"
    large = "large"


@deprecated("теперь через rabbitmq")
async def transcribe_audio_async(audio_file_path: str, user_id: int, record_id: int, model: str = Models.base):
    headers = {"secret-key": SECRET_KEY}
    params = {"file": audio_file_path, "model": model}
    async with aiohttp.ClientSession() as session:
        async with session.get(WHISPER_API_URL + "transcription/get_transcription", headers=headers, params=params) as response:
            if response.status not in (status.HTTP_200_OK, status.HTTP_201_CREATED, 204):
                raise Exception(f"Error {response.status}: {await response.text()}")
            transcription = await response.json()["transcription"]
            return await Repository.update_transcription(user_id, record_id, transcription)


@deprecated("теперь через rabbitmq")
async def add_task_transcribe_async(audio_file_path: str, user_id: int, record_id: int, model: str = Models.base):
    headers = {"secret-key": SECRET_KEY}
    params = {"file": audio_file_path, "user_id": user_id,
              "record_id": record_id, "model": model}
    async with aiohttp.ClientSession() as session:
        async with session.get(WHISPER_API_URL + "transcription/add_task_transcription", headers=headers, params=params) as response:
            if response.status not in (status.HTTP_200_OK, status.HTTP_201_CREATED, 204):
                return "Not found"
            return await response.json()


@deprecated("теперь через rabbitmq")
async def get_task_status_async(task_id: str):
    headers = {"secret-key": SECRET_KEY}
    params = {"task_id": task_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(WHISPER_API_URL + "transcription/get_task_status", headers=headers, params=params) as response:
            if response.status not in (status.HTTP_200_OK, status.HTTP_201_CREATED, 204):
                return "Not found"
            return await response.json()
