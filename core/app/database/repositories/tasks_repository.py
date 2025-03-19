from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import TaskOrm, WorkTypesOrm
from .base_repository import BaseRepository
import logging


class TasksRepository(BaseRepository):
    """
    Класс репозиторий для работы с задачами в базе данных.
    """

    @staticmethod
    def repository_factory():
        return TasksRepository()

    async def get_all_tasks_by_user_id(self, user_id: str, completed: bool) -> list[TaskOrm] | None:
        """Возвращает все задачи, связанные с пользователем, с учетом статуса выполнения."""
        try:
            async with self.session:
                query = select(TaskOrm).where(TaskOrm.user_id ==
                                              user_id, TaskOrm.is_completed == completed)
                result = await self.session.execute(query)
                return list(result.scalars().all())
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def add_task(self, data: TaskOrm) -> str | None:
        """Добавляет новую задачу в базу данных."""
        try:
            async with self.session:
                new_task = TaskOrm(
                    user_id=data.user_id,
                    work_type=data.work_type,
                    description=data.description,
                    created_at=data.created_at,
                    duration_seconds=data.duration_seconds,
                    is_completed=False
                )
                self.session.add(new_task)
                await self.session.commit()
                return new_task.id
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def soft_delete_task(self, task_id: str) -> bool:
        """Удаляет задачу из базы данных (помечает как выполненную)."""
        try:
            async with self.session:
                task_to_delete = await self.session.get(TaskOrm, task_id)
                if task_to_delete:
                    # if task_to_delete.work_type != WorkTypesOrm.OTHER:
                    #     await self.session.delete(task_to_delete)
                    # else:
                    #     task_to_delete.is_completed = True
                    task_to_delete.is_completed = True
                    await self.session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False
