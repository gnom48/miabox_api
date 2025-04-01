from fastapi import APIRouter, HTTPException, Depends, status
from app.database.repositories import TasksRepository
from app.api.models import Task, UserCredentials
from app.api.middlewares import get_user_from_request

router_tasks = APIRouter(prefix="/tasks", tags=["Задачи"])


@router_tasks.get("/", status_code=status.HTTP_200_OK)
async def get_tasks(
    user_credentials: UserCredentials = Depends(get_user_from_request),
    tasks_repository: TasksRepository = Depends(
        TasksRepository.repository_factory)
):
    async with tasks_repository:
        tasks = await tasks_repository.get_all_tasks_by_user_id(user_credentials.id, False)
        if tasks is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found")
        return tasks


@router_tasks.get("/completed", status_code=status.HTTP_200_OK)
async def get_completed_tasks(
    user_credentials: UserCredentials = Depends(get_user_from_request),
    tasks_repository: TasksRepository = Depends(
        TasksRepository.repository_factory)
):
    async with tasks_repository:
        tasks = await tasks_repository.get_all_tasks_by_user_id(user_credentials.id, True)
        if tasks is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Completed tasks not found")
        return tasks


@router_tasks.post("/", status_code=status.HTTP_201_CREATED)
async def add_task(
    task: Task,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    tasks_repository: TasksRepository = Depends(
        TasksRepository.repository_factory)
):
    async with tasks_repository:
        task_id = await tasks_repository.add_task(task)
        if not task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to insert task")
        return task_id


@router_tasks.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: str,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    tasks_repository: TasksRepository = Depends(
        TasksRepository.repository_factory)
):
    async with tasks_repository:
        success = await tasks_repository.soft_delete_task(task_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Task not found or unable to delete")
        return {"detail": "Task deleted successfully"}
