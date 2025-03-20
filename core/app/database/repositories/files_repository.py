from enum import Enum
from sqlalchemy.sql import text
from app.database.models import FileOrm, FilesAccessOrm, FileAccessModeOrm
from sqlalchemy import select, update, delete, insert, and_
from .base_repository import BaseRepository
import logging


class FilesRepository(BaseRepository):
    """
    Класс репозиторий для работы с базой данных как с объектом
    """

    @staticmethod
    def repository_factory():
        return FilesRepository()

    async def add_file(self, obj_name: str, bucket_name: str, user_id: str) -> str:
        """Добавляет файл в базу данных и связывает его с пользователем."""
        try:
            async with self.session:
                new_file = FileOrm(
                    obj_name=obj_name,
                    bucket_name=bucket_name
                )
                self.session.add(new_file)
                await self.session.commit()

                await self.add_access_to(user_id, new_file.id)

                return new_file.id
        except Exception as e:
            logging.error(e.__str__())
            return None

    async def check_access(self, access: Enum, user_id: str, file_id: str) -> bool:
        """Проверяет доступ к файлу."""
        try:
            async with self.session:
                select_request = select(FilesAccessOrm).where(
                    FilesAccessOrm.file_id == file_id)
                access_records = await self.session.execute(select_request)
                file_access_list = list(access_records.scalars().all())
                if access.name == FileAccessModeOrm.WRITE.name:
                    return any(item.user_id == user_id and item.file_access_mode.name == access.name for item in file_access_list)
                else:
                    return any(item.user_id == user_id for item in file_access_list)
        except Exception as e:
            logging.error(e.__str__())
            return None

    async def add_access_to(self, user_id: str, file_id: str) -> bool:
        """Предоставляет пользователю доступ к файлу."""
        try:
            async with self.session:
                access_record = FilesAccessOrm(
                    user_id=user_id,
                    file_id=file_id,
                    file_access_mode=FileAccessModeOrm.WRITE
                )
                self.session.add(access_record)
                await self.session.commit()
                return True
        except Exception as e:
            logging.error(e.__str__())
            return None

    async def get_file_access(self, file_id: str) -> list[FilesAccessOrm]:
        """Возвращает пользователей, у которых есть доступ к файлу."""
        try:
            async with self.session:
                select_request = select(FilesAccessOrm).where(
                    FilesAccessOrm.file_id == file_id)
                access_records = await self.session.execute(select_request)
                return list(access_records.scalars().all())
        except Exception as e:
            logging.error(e.__str__())
            return None

    async def get_file_info_by_id(self, file_id: str) -> FileOrm:
        """Возвращает запись информации о файле."""
        try:
            async with self.session:
                return await self.session.get(FileOrm, file_id)
        except Exception as e:
            logging.error(e.__str__())
            return None

    async def delete_file(self, file_id: str) -> bool:
        """Убирает доступ у пользователя к файлу."""
        try:
            async with self.session:
                file_to_del = await self.session.get(FileOrm, file_id)
                await self.session.delete(file_to_del)
                await self.session.commit()
                return True
        except Exception as e:
            logging.error(e.__str__())
            return None

    async def deny_access_to(self, user_id: str, file_id: str) -> bool:
        """Убирает доступ у пользователя к файлу."""
        try:
            async with self.session:
                stmt = delete(FilesAccessOrm).where(
                    FilesAccessOrm.user_id == user_id,
                    FilesAccessOrm.file_id == file_id
                )
                result = await self.session.execute(stmt)
                await self.session.commit()
                return result.rowcount > 0
        except Exception as e:
            logging.error(e.__str__())
            return None
