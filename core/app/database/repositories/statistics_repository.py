from enum import Enum
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import StatisticOrm, WorkTypesOrm, KpiOrm, KpiLevelsOrm
from .base_repository import BaseRepository
import logging


class StatisticsRepository(BaseRepository):
    """
    Класс репозиторий для работы с записями звонков в базе данных.
    """

    @staticmethod
    def repository_factory():
        return StatisticsRepository()

    async def add_statistics_record(self, stat: StatisticOrm) -> str | None:
        """Добавляет запись статистики в базу данных."""
        try:
            async with self.session:
                new_stat_record = StatisticOrm(
                    user_id=stat.user_id,
                    date_time=stat.date_time,
                    work_type=stat.work_type,
                    comment=stat.comment,
                    count=stat.count,
                    is_archive=stat.is_archive
                )
                self.session.add(new_stat_record)
                await self.session.commit()
                return new_stat_record.id
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def get_statistics_in_period(self, user_id: str, start: int, end: int) -> dict[WorkTypesOrm | str, int]:
        """Возвращает статистику за период от start до end."""
        try:
            async with self.session:
                query = (
                    select(
                        StatisticOrm.work_type,
                        func.sum(StatisticOrm.count).label('total_count')
                    )
                    .where(StatisticOrm.user_id == user_id)
                    .where(StatisticOrm.date_time >= start)
                    .where(StatisticOrm.date_time <= end)
                    .group_by(StatisticOrm.work_type)
                )
                records = await self.session.execute(query)
                all_works = records.fetchall()
                return {work_type: total_count for work_type, total_count in all_works}
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def get_last_month_kpi(self, user_id: str) -> KpiOrm:
        """Возвращает установленный за прошлый месяц KPI."""
        try:
            async with self.session:
                return await self.session.get(KpiOrm, user_id)
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return None

    async def set_kpi_level(self, kpi: KpiOrm) -> bool:
        """Устанавливает KPI вручную. Если не было записи - создаст"""
        try:
            async with self.session:
                current_kpi = await self.session.get(KpiOrm, kpi.user_id)
                if not current_kpi:
                    self.session.add(
                        KpiOrm(
                            user_id=kpi.user_id,
                            kpi_level=kpi.kpi_level,
                            base_salary_percentage=kpi.base_salary_percentage,
                            kpi=kpi.kpi
                        )
                    )
                else:
                    current_kpi.user_id = kpi.user_id
                    current_kpi.kpi_level = kpi.kpi_level
                    current_kpi.base_salary_percentage = kpi.base_salary_percentage
                    current_kpi.kpi = kpi.kpi
                await self.session.commit()
                return True
        except SQLAlchemyError as e:
            logging.error(e.__str__())
            return False

    def get_kpi_level(self, total_deals_count: int, top_flag: bool = False) -> tuple:
        """Возвращает кортеж типа (уровнь KPI, базовый процент зп)."""
        if top_flag and total_deals_count >= 21:
            return (KpiLevelsOrm.TOP, 50)
        elif total_deals_count <= 3:
            return (KpiLevelsOrm.TRAINEE, 40)
        elif total_deals_count >= 3 and total_deals_count <= 20:
            return (KpiLevelsOrm.SPECIALIST, 43)
        elif total_deals_count > 21:
            return (KpiLevelsOrm.EXPERT, 45)
