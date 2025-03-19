from sqlalchemy.exc import SQLAlchemyError
from app.database.models import UserOrm, UserTypesOrm
from .base_repository import BaseRepository
import logging


class UsersRepository(BaseRepository):
    """
    Класс репозиторий для работы с пользователями в базе данных.
    """

    @staticmethod
    def repository_factory():
        return UsersRepository()

    async def update_user(self, data: UserOrm) -> bool:
        """Редактирует информацию о пользователе в базе данных."""
        try:
            async with self.session:
                user_to_update = await self.session.get(UserOrm, data.id)
                if user_to_update:
                    user_to_update.type = UserTypesOrm[data.type.name]
                    user_to_update.birthday = data.birthday
                    user_to_update.gender = data.gender
                    user_to_update.name = data.name
                    user_to_update.phone = data.phone
                    user_to_update.email = data.email
                    await self.session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False

    async def update_avatar_only(self, user_id: str, new_avatar_file_id: str) -> bool:
        """Редактирует информацию о пользователе в базе данных."""
        try:
            async with self.session:
                user_to_update = await self.session.get(UserOrm, user_id)
                user_to_update.image = new_avatar_file_id
                await self.session.commit()
                return True
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False

    async def get_user_by_id(self, user_id: str) -> UserOrm | None:
        """Возвращает пользователя по его идентификатору."""
        try:
            async with self.session:
                return await self.session.get(UserOrm, user_id)
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None
