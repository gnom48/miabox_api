from fastapi import APIRouter, HTTPException, Header, Response, UploadFile
from .consts import SECRET_KEY
from .trascription import AsyncWhisper, Models


async_whisper: AsyncWhisper = AsyncWhisper()
router_transcription = APIRouter(prefix="/transcription", tags=["Транскрипция"])


@router_transcription.get("/get_transcription")
async def get_transcription(file: str, model: str = "base", secret_key: str | None = Header(default=None)):
    if not secret_key or secret_key != SECRET_KEY:
        raise HTTPException(status_code=400, detail="uncorrect header")
    if file == "" or file is None:
        raise HTTPException(status_code=404, detail="no file to transcribe")
    if async_whisper.model_name != model:
        await async_whisper.initialize_async(model)
    return await async_whisper.transcribe_async(file_name=file)


