from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import CallOrm, FileOrm
from .base_repository import BaseRepository
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api.models import Call


class CallsRepository(BaseRepository):
    """
    Класс репозиторий для работы с записями звонков в базе данных.
    """

    @staticmethod
    def repository_factory():
        return CallsRepository()

    async def add_call_record_to_storage(self, call: 'Call') -> str | None:
        """Добавляет запись звонка в базу данных."""
        from app.api.models import Call
        try:
            async with self.session:
                user_call = CallOrm(**call.model_dump())
                user_call.id = None
                self.session.add(user_call)
                await self.session.commit()
                return user_call.id
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def get_all_info_user_calls(self, user_id: str) -> list[CallOrm] | None:
        """Возвращает информацию о всех звонках пользователя."""
        try:
            async with self.session:
                query = select(CallOrm).where(CallOrm.user_id == user_id)
                result = await self.session.execute(query)
                return list(result.scalars().all())
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def update_transcription(self, call_id: str, transcription: str) -> bool:
        """Обновляет транскрипцию звонка."""
        try:
            async with self.session:
                user_call = await self.session.get_one(CallOrm, call_id)
                if user_call:
                    user_call.transcription = transcription
                    await self.session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False

    async def get_one_call(self, call_id: str) -> CallOrm:
        """Возвращает информацию о звонке пользователя."""
        try:
            async with self.session:
                user_call = await self.session.get_one(CallOrm, call_id)
                if user_call:
                    return user_call
                return None
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None
