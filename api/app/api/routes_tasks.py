from fastapi import APIRouter, HTTPException, Header, Request
from .models import Task
from .jwt import verify_jwt_token
from api.app.repository import *


router_tasks = APIRouter(prefix="/task", tags=["Задачи"])

@router_tasks.get("/all", status_code=200)
async def task_all(token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    return await Repository.get_all_tasks_by_user_id(user.id, False)


@router_tasks.get("/completed", status_code=200)
async def task_all(token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    return await Repository.get_all_tasks_by_user_id(user.id, True)
    

@router_tasks.post("/add", status_code=201)
async def task_add(req: Request, task: Task, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    if not user:
        raise HTTPException(status_code=401, detail="not found user")
    task_id = await Repository.add_task(task)
    if not task_id:
        raise HTTPException(status_code=402, detail="unable to insert")
    return task_id


@router_tasks.delete("/delete", status_code=200)
async def task_delete(req: Request, task_id: int, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = await verify_jwt_token(token_authorization)
    if not user:
        raise HTTPException(status_code=404, detail="not found user")
    return await Repository.del_task(task_id)