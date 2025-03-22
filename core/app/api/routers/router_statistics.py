import time
from fastapi import APIRouter, HTTPException, Header, Depends, status
from app.api.middlewares import get_user_from_request
from app.api.models import UserCredentials, Statistic, StatisticAggregated, KpiSummary, Kpi, WorkTypes
from app.database.repositories import StatisticsRepository
from app.utils.kpi_calculator import KpiCalculator
import datetime


router_statistics = APIRouter(prefix="/user/statistics", tags=["Статистика"])


@router_statistics.get("/aggregated", status_code=status.HTTP_200_OK)
async def user_statistics_get(
    start: int,
    end: int,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    statistics_repository: StatisticsRepository = Depends(
        StatisticsRepository.repository_factory)
):
    async with statistics_repository:
        res = await statistics_repository.get_statistics_in_period(user_credentials.id, start, end)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Sequence contains no elements")
        return StatisticAggregated(
            user_id=user_credentials.id,
            start=start,
            end=end,
            works=res
        )


@router_statistics.get("/kpi", status_code=status.HTTP_200_OK)
async def user_statistics_get_with_kpi(
    user_credentials: UserCredentials = Depends(get_user_from_request),
    statistics_repository: StatisticsRepository = Depends(
        StatisticsRepository.repository_factory)
):
    async with statistics_repository:
        last_month_kpi = await statistics_repository.get_last_month_kpi(user_credentials.id)
        if not last_month_kpi:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Sequence contains no elements")
        now = datetime.datetime.now()
        first_day_of_month = datetime.datetime(now.year, now.month, 1)
        start_unix = int(time.mktime(first_day_of_month.timetuple()))
        if now.month == 12:
            last_day_of_month = datetime.datetime(
                now.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            last_day_of_month = datetime.datetime(
                now.year, now.month + 1, 1) - datetime.timedelta(days=1)
        end_unix = int(time.mktime(last_day_of_month.timetuple()))
        # NOTE: здесь start и end - это первое и последнее число текущего календарного месяца
        data = await statistics_repository.get_statistics_in_period(user_credentials.id, start_unix, end_unix)
        kpi_calc = KpiCalculator(last_month_kpi.base_salary_percentage, last_month_kpi.kpi_level, data.deals_rent, data.deals_sale, data.regular_contracts,
                                 data.exclusive_contracts, data.calls, data.meets, data.flyers, data.analytics, 0, user.type)
        return KpiSummary(
            last_month_kpi=last_month_kpi.kpi,
            current_month_kpi=kpi_calc.calculate_kpi(),
            level=last_month_kpi.kpi_level,
            summary_deals_rent=data[WorkTypes.DEAL_RENT.name],
            summary_deals_sale=data[WorkTypes.DEAL_SALE.name]
        )


@router_statistics.put("/manually_set_kpi", status_code=status.HTTP_200_OK)
async def user_statistics_kpi_move(
    kpi: Kpi,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    statistics_repository: StatisticsRepository = Depends(
        StatisticsRepository.repository_factory)
):
    async with statistics_repository:
        res = await statistics_repository.set_kpi_level(kpi)
        if res == None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="move level error")
        return res
