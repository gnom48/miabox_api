import aiohttp
from api.app.database.consts import WHISPER_API_URL
from api.app.repository import Repository


async def transcribe_audio_async(audio_file_path: str, user_id: int, record_id: int, model: str = "base"):
    headers = {"secret-key": "miabox"}
    params = {"file": audio_file_path, "model": model}
    async with aiohttp.ClientSession() as session:
        async with session.get(WHISPER_API_URL + "get_transcription", headers=headers, params=params) as response:
            if response.status != 200:
                raise Exception(f"Error {response.status}: {await response.text()}")
            transcription = await response.json()["transcription"]
            return await Repository.update_transcription(user_id, record_id, transcription)