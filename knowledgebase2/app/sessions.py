import uuid
import time
from fastapi import HTTPException, status
from app.redis_client import RedisClient
from typing import Any, Dict, Union
from pydantic import BaseModel
from app.models import SessionData


class SessionManager:
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def create_session(self, session_data: SessionData) -> str:
        """
        Создает новую сессию и возвращает UUID сессии.
        """
        session_uuid = str(uuid.uuid4())
        serialized_data = session_data.model_dump_json()
        await self.redis_client.set(session_uuid, serialized_data)
        return session_uuid

    async def get_session(self, session_uuid: str) -> Union[SessionData, None]:
        """
        Получает данные сессии по UUID.
        """
        raw_data = await self.redis_client.get(session_uuid)
        if raw_data is None:
            return None
        return SessionData.model_validate_json(raw_data)

    async def update_session(self, session_uuid: str, new_data: SessionData):
        """
        Обновляет существующую сессию новыми данными.
        """
        serialized_data = new_data.model_dump_json()
        await self.redis_client.set(session_uuid, serialized_data)

    async def invalidate_session(self, session_uuid: str):
        """
        Удаляет сессию по UUID.
        """
        await self.redis_client.delete(session_uuid)

    async def cleanup_expired_sessions(self):
        """
        Периодическая очистка устаревших сессий
        """
        # TODO: Перебирать все сессии и если SessionData.created_at старый, то удалять
        pass
