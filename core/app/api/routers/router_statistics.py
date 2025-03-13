from fastapi import APIRouter, HTTPException, Header, Depends, status
from api.models import UserKpiLevels
from app.database import Repository
from app.api import get_user_from_request, UserCredentials


router_statistics = APIRouter(prefix="/user/statistics", tags=["Статистика"])


@router_statistics.get("/get", status_code=status.HTTP_200_OK)
async def user_statistics_get(period: str, user_credentials: UserCredentials | None = Depends(get_user_from_request)):
    res = await Repository.get_statistics_by_period(user_credentials.id, period)
    return res


@router_statistics.get("/get_kpi", status_code=status.HTTP_200_OK)
async def user_statistics_get_with_kpi(user_credentials: UserCredentials | None = Depends(get_user_from_request)):
    last_month_kpi = await Repository.get_statistics_with_kpi(user_credentials.id)
    current_month_kpi = await Repository.get_current_kpi(user_credentials.id)
    if current_month_kpi is None:
        return {"last_month_kpi": last_month_kpi, "current_month_kpi": None, "level": None, "summary_deals_rent": None, "summary_deals_sale": None}
    return {
        "last_month_kpi": last_month_kpi,
        "current_month_kpi": current_month_kpi["kpi"],
        "level": current_month_kpi["level"],
        "summary_deals_rent": current_month_kpi["deals_rent"],
        "summary_deals_sale": current_month_kpi["deals_sale"]
    }


@router_statistics.put("/update", status_code=status.HTTP_200_OK)
async def user_statistics_update(statistic: str, addvalue: int, user_credentials: UserCredentials | None = Depends(get_user_from_request)):
    res = await Repository.update_statistics(user_credentials.id, statistic, addvalue)
    return res


@router_statistics.put("/move_kpi_level", status_code=status.HTTP_200_OK)
async def user_statistics_kpi_move(level: UserKpiLevels, user_credentials: UserCredentials | None = Depends(get_user_from_request)):
    res = await Repository.update_kpi_level(user_credentials.id, level)
    if res == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="move level error")
    return res
