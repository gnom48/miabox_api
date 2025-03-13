from fastapi import APIRouter, HTTPException, Header, Request, Depends, status
from api.models import Task
from app.database import *
from app.api import get_user_from_request, UserCredentials


router_tasks = APIRouter(prefix="/task", tags=["Задачи"])


@router_tasks.get("/all", status_code=status.HTTP_200_OK)
async def task_all(user_credentials: UserCredentials | None = Depends(get_user_from_request)):
    return await Repository.get_all_tasks_by_user_id(user_credentials.id, False)


@router_tasks.get("/completed", status_code=status.HTTP_200_OK)
async def task_all(user_id: str, user_credentials: UserCredentials | None = Depends(get_user_from_request)):
    return await Repository.get_all_tasks_by_user_id(user_id, True)


@router_tasks.post("/add", status_code=status.HTTP_201_CREATED)
async def task_add(task: Task, user_credentials: UserCredentials | None = Depends(get_user_from_request)):
    task_id = await Repository.add_task(task)
    if not task_id:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="unable to insert")
    return task_id


@router_tasks.delete("/delete", status_code=status.HTTP_200_OK)
async def task_delete(task_id: str, user_credentials: UserCredentials | None = Depends(get_user_from_request)):
    return await Repository.del_task(task_id)
