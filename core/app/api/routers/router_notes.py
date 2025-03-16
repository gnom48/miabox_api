from fastapi import APIRouter, HTTPException, Header, Request, Depends, status
from app.database import Repository
from api.models import Note
from app.api import get_user_from_request, UserCredentials


router_notes = APIRouter(prefix="/note", tags=["Заметки"])


@router_notes.get("/all", status_code=status.HTTP_200_OK)
async def notes_all(user_credentials: UserCredentials = Depends(get_user_from_request)):
    return await Repository.get_all_notes_by_user_id(user.id)


@router_notes.post("/add", status_code=status.HTTP_201_CREATED)
async def note_add(note: Note, user_credentials: UserCredentials = Depends(get_user_from_request)):
    note_id = await Repository.add_note(note)
    if not note_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="unable to insert")
    return note_id


@router_notes.delete("/delete", status_code=status.HTTP_200_OK)
async def note_delete(note_id: str, user_credentials: UserCredentials = Depends(get_user_from_request)):
    return await Repository.del_note(note_id)


@router_notes.put("/edit", status_code=status.HTTP_200_OK)
async def note_edit(note: Note, user_credentials: UserCredentials = Depends(get_user_from_request)):
    return await Repository.edit_note(note)
