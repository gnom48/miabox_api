from fastapi import APIRouter, HTTPException, Depends, status
from app.database.repositories import NotesRepository
from app.api.models import Note, UserCredentials
from app.api.middlewares import get_user_from_request

router_notes = APIRouter(prefix="/notes", tags=["Заметки"])


@router_notes.get("/", status_code=status.HTTP_200_OK, description="Возвращает все заметки текущего пользователя")
async def get_notes(
    user_credentials: UserCredentials = Depends(get_user_from_request),
    notes_repository: NotesRepository = Depends(
        NotesRepository.repository_factory)
):
    async with notes_repository:
        notes = await notes_repository.get_all_notes_by_user_id(user_credentials.id)
        if notes is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Notes not found")
        return notes


@router_notes.post("/", status_code=status.HTTP_201_CREATED, description="Создает заметку для текущего пользователя")
async def add_note(
    note: Note,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    notes_repository: NotesRepository = Depends(
        NotesRepository.repository_factory)
):
    async with notes_repository:
        note_id = await notes_repository.add_note(note)
        if not note_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to insert note")
        return note_id


@router_notes.delete("/{note_id}", status_code=status.HTTP_200_OK, description="Удаляет заметку по Id")
async def delete_note(
    note_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    notes_repository: NotesRepository = Depends(
        NotesRepository.repository_factory)
):
    async with notes_repository:
        success = await notes_repository.delete_note(note_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Note not found or unable to delete")
        return {"detail": "Note deleted successfully"}


@router_notes.put("/", status_code=status.HTTP_200_OK, description="Обновляет заметку по Id")
async def update_note(
    note: Note,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    notes_repository: NotesRepository = Depends(
        NotesRepository.repository_factory)
):
    async with notes_repository:
        success = await notes_repository.edit_note(note)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to update note")
        return {"detail": "Note updated successfully"}
