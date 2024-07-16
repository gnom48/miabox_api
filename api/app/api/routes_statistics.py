from fastapi import APIRouter, HTTPException, Header, Request
from .models import User, Statistics
from ..repository import *
from datetime import datetime
from .jwt import create_jwt_token, verify_jwt_token


router_statistics = APIRouter(prefix="/user/statistics", tags=["Статистика"])

    
@router_statistics.get("/get", status_code=200)
async def user_statistics_get(period: str, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    res = await Repository.get_statistics_by_period(user.id, period)
    return res


@router_statistics.get("/get_kpi", status_code=200)
async def user_statistics_get_with_kpi(token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    res = await Repository.get_statistics_with_kpi(user.id)
    return res


@router_statistics.put("/update", status_code=200)
async def user_statistics_update(statistic: str, addvalue: int, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    res = await Repository.update_statistics(user.id, statistic, addvalue)
    return res


@router_statistics.put("/move_kpi_level", status_code=200)
async def user_statistics_kpi_move(level: UserKpiLevels, token_authorization: str | None = Header(default=None)):
    if not token_authorization:
        raise HTTPException(status_code=400, detail="uncorrect header")
    user = await verify_jwt_token(token_authorization)
    res = await Repository.update_kpi_level(user.id, level)
    if res == None:
        raise HTTPException(status_code=401, detail="move level error")
    return res