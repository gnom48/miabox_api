from fastapi import APIRouter, HTTPException, Header, Request
from api.app.repository import *
# from ..repository import *
from .models import Note
from .jwt import verify_jwt_token


router_notes = APIRouter(prefix="/note", tags=["Заметки"])


@router_notes.get("/all", status_code=200)
async def notes_all(token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="incorrect header")
    user = await verify_jwt_token(token_authorization)
    return await Repository.get_all_notes_by_user_id(user.id)


@router_notes.post("/add", status_code=201)
async def note_add(req: Request, note: Note, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="incorrect header")
    user = await verify_jwt_token(token_authorization)
    if not user:
        raise HTTPException(status_code=404, detail="not found user")
    note_id = await Repository.add_note(note)
    if not note_id:
        raise HTTPException(status_code=401, detail="unable to insert")
    return note_id


@router_notes.delete("/delete", status_code=200)
async def note_delete(req: Request, note_id: int, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="incorrect header")
    user = await verify_jwt_token(token_authorization)
    if not user:
        raise HTTPException(status_code=404, detail="not found user")
    return await Repository.del_note(note_id)



@router_notes.put("/edit", status_code=200)
async def note_edit(req: Request, note: Note, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="incorrect header")
    user = await verify_jwt_token(token_authorization)
    if not user:
        raise HTTPException(status_code=404, detail="not found user")
    return await Repository.edit_note(note)
