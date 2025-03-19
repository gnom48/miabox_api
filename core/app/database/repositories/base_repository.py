from ..orm import new_session
from app.database.models import VersionOrm
from sqlalchemy.sql import text, select
import logging


class BaseRepository:
    """Класс репозиторий для работы с базой данных как с объектом"""

    def __init__(self):
        self.session = new_session()

    async def dispose(self):
        """Закрывает сессию"""
        await self.session.close()

    async def __aenter__(self):
        logging.debug("Сессия открыта")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logging.debug("Сессия закрыта")
        await self.dispose()

    @staticmethod
    def repository_factory():
        return BaseRepository()

    # -------------------------- config --------------------------

    @classmethod
    async def get_config(cls) -> tuple:
        async with new_session() as session:
            try:
                req = text("SELECT version() AS db_version;")
                result = await session.execute(req)
                version = result.scalars().first()
                req = text("SELECT now() AS db_datetime;")
                result = await session.execute(req)
                ntime = result.scalars().first()
                return (version, ntime)
            except:
                return None

    @classmethod
    async def get_supported_versions(cls) -> list[VersionOrm]:
        async with new_session() as session:
            try:
                req = select(VersionOrm)
                result = await session.execute(req)
                return list(result.scalars().all())
            except:
                return None
