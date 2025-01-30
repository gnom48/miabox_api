import aiohttp
from .consts import *


async def put_transcribe_result_async(transcription: str, user_id: str, record_id: str):
    headers = {"secret-key": SECRET_KEY}
    data = {"transcription": transcription["text"], "user_id": user_id, "record_id": record_id}
    async with aiohttp.ClientSession() as session:
        async with session.put(url=MAIN_API_URL + "calls/update_transcription", headers=headers, params=data) as response:
            if response.status not in (200, 201, 204):
                raise Exception(f"Error {response.status}: {await response.text()}")
            return await response.json()