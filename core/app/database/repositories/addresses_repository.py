from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import AddressOrm
from .base_repository import BaseRepository
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api.models import Address


class AddressesRepository(BaseRepository):
    """
    Класс репозиторий для работы с адресами в базе данных.
    """

    @staticmethod
    def repository_factory():
        return AddressesRepository()

    async def add_address_info(self, data: 'Address') -> str:
        """Добавляет информацию об адресе в базу данных."""
        try:
            async with self.session:
                address_info_orm = AddressOrm(**data.model_dump())
                address_info_orm.id = None
                self.session.add(address_info_orm)
                await self.session.commit()
                return address_info_orm.id
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def get_address_info_by_user_id(self, user_id: str, date_start: int | None = None, date_end: int | None = None) -> list[AddressOrm]:
        """Возвращает адреса, связанные с пользователем, с возможностью фильтрации по дате."""
        try:
            async with self.session:
                query = select(AddressOrm).where(AddressOrm.user_id == user_id)
                if date_start is not None:
                    query = query.where(AddressOrm.date_time >= date_start)
                if date_end is not None:
                    query = query.where(AddressOrm.date_time <= date_end)
                result = await self.session.execute(query)
                addresses = result.scalars().all()
                return list(addresses)
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def delete_address_info(self, address_id: str) -> bool:
        """Удаляет информацию об адресе из базы данных."""
        try:
            async with self.session:
                stmt = delete(AddressOrm).where(AddressOrm.id == address_id)
                result = await self.session.execute(stmt)
                await self.session.commit()
                return result.rowcount > 0
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False
