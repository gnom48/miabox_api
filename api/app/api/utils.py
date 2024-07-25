import aiohttp
from api.app.database.consts import WHISPER_API_URL, SECRET_KEY
from api.app.repository import Repository


async def transcribe_audio_async(audio_file_path: str, user_id: int, record_id: int, model: str = "base"):
    headers = {"secret-key": SECRET_KEY}
    params = {"file": audio_file_path, "model": model}
    async with aiohttp.ClientSession() as session:
        async with session.get(WHISPER_API_URL + "get_transcription", headers=headers, params=params) as response:
            if response.status not in (200, 201, 204):
                raise Exception(f"Error {response.status}: {await response.text()}")
            transcription = await response.json()["transcription"]
            return await Repository.update_transcription(user_id, record_id, transcription)
        

async def add_task_transcribe_async(audio_file_path: str, user_id: int, record_id: int, model: str = "base"):
    headers = {"secret-key": SECRET_KEY}
    params = {"file": audio_file_path, "user_id": user_id, "record_id": record_id, "model": model}
    async with aiohttp.ClientSession() as session:
        async with session.get(WHISPER_API_URL + "add_task_transcription", headers=headers, params=params) as response:
            if response.status not in (200, 201, 204):
                raise Exception(f"Error {response.status}: {await response.text()}")
            return await response.json()
        
        
async def get_task_status_async(task_id: str):
    headers = {"secret-key": SECRET_KEY}
    params = {"task_id": task_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(WHISPER_API_URL + "get_task_status", headers=headers, params=params) as response:
            if response.status not in (200, 201, 204):
                raise Exception(f"Error {response.status}: {await response.text()}")
            return await response.json()