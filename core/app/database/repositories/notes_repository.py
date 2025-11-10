from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import NoteOrm
from .base_repository import BaseRepository
import logging
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api.models import Note


class NotesRepository(BaseRepository):
    """
    Класс репозиторий для работы с заметками в базе данных.
    """

    @staticmethod
    def repository_factory():
        return NotesRepository()

    async def get_all_notes_by_user_id(self, user_id: str) -> list[NoteOrm] | None:
        """Возвращает все заметки, связанные с пользователем."""
        try:
            async with self.session:
                query = select(NoteOrm).where(NoteOrm.user_id == user_id)
                result = await self.session.execute(query)
                return list(result.scalars().all())
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def add_note(self, data: 'Note') -> str | None:
        """Добавляет новую заметку в базу данных."""
        from app.api.models import Note
        try:
            async with self.session:
                new_note = NoteOrm(
                    **data.model_dump()
                )
                new_note.id = None
                self.session.add(new_note)
                await self.session.commit()
                return new_note.id
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def delete_note(self, note_id: str) -> bool:
        """Удаляет заметку из базы данных."""
        try:
            async with self.session:
                note_to_delete = await self.session.get(NoteOrm, note_id)
                if note_to_delete:
                    await self.session.delete(note_to_delete)
                    await self.session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False

    async def edit_note(self, data: 'Note') -> bool:
        """Редактирует существующую заметку в базе данных."""
        from app.api.models import Note
        try:
            async with self.session:
                note_to_edit = await self.session.get(NoteOrm, data.id)
                if note_to_edit:
                    note_to_edit.title = data.title
                    note_to_edit.description = data.description
                    note_to_edit.created_at = data.created_at
                    await self.session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False
