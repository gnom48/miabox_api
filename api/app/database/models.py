from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, Column, Integer, LargeBinary, String, Float
from datetime import datetime
from enum import Enum
from typing import Annotated


class BaseModelOrm(DeclarativeBase):
    pass


class UserTypesOrm(Enum):
    COMMERCIAL = "Риелтер коммерческой недвижимости"
    PRIVATE = "Риелтер частной недвижимости"
    
    
class WorkTasksTypesOrm(Enum):
    FLYERS = "Рассклейка"
    CALLS = "Обзвон"
    SHOW = "Показ объекта"
    MEET = "Встреча по объекту"
    DEAL = "Сделка"
    DEPOSIT = "Получение задатка"
    SEARCH = "Поиск объектов"
    ANALYTICS = "Аналитика рынка"
    OTHER = "Нечто особенное"


class ImageOrm(BaseModelOrm):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    data = Column(LargeBinary)


class UserOrm(BaseModelOrm):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, unique=True)
    password: Mapped[str]
    type: Mapped[UserTypesOrm]
    photo: Mapped[str]
    reg_date: Mapped[int]
    name = Column(String, default="Пользователь")
    gender: Mapped[str | None]
    birthday: Mapped[int | None]
    phone: Mapped[str | None]
    image: Mapped[int] = mapped_column(ForeignKey(ImageOrm.id), default=1)


class NoteOrm(BaseModelOrm):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str]
    desc: Mapped[str | None]
    date_time: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"))
    notification_id: Mapped[int]


class TaskOrm(BaseModelOrm):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_type: Mapped[WorkTasksTypesOrm]
    desc: Mapped[str | None]
    date_time: Mapped[int]
    duration_seconds: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"))
    notification_id: Mapped[int]
    

class TeamOrm(BaseModelOrm):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str]
    created_date_time = Mapped[int]
    

class UserStatusesOrm(Enum):
    OWNER = "Владелец"
    USER = "Участник"
    
    
class UserTeamOrm(BaseModelOrm):
    __tablename__ = "user_teams"
    team_id: Mapped[int] = mapped_column(ForeignKey(TeamOrm.id, ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    role: Mapped[UserStatusesOrm]


class DayStatisticsOrm(BaseModelOrm):
    __tablename__ = "day_statistics"
    user_id: Mapped[int] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    flyers = Column(Integer, default=0)
    calls = Column(Integer, default=0)
    shows = Column(Integer, default=0)
    meets = Column(Integer, default=0)
    deals = Column(Integer, default=0)
    deposits = Column(Integer, default=0)
    searches = Column(Integer, default=0)
    analytics = Column(Integer, default=0)
    others = Column(Integer, default=0)


class WeekStatisticsOrm(BaseModelOrm):
    __tablename__ = "week_statistics"
    user_id: Mapped[int] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    flyers = Column(Integer, default=0)
    calls = Column(Integer, default=0)
    shows = Column(Integer, default=0)
    meets = Column(Integer, default=0)
    deals = Column(Integer, default=0)
    deposits = Column(Integer, default=0)
    searches = Column(Integer, default=0)
    analytics = Column(Integer, default=0)
    others = Column(Integer, default=0)


class MonthStatisticsOrm(BaseModelOrm):
    __tablename__ = "month_statistics"
    user_id: Mapped[int] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    flyers = Column(Integer, default=0)
    calls = Column(Integer, default=0)
    shows = Column(Integer, default=0)
    meets = Column(Integer, default=0)
    deals = Column(Integer, default=0)
    deposits = Column(Integer, default=0)
    searches = Column(Integer, default=0)
    analytics = Column(Integer, default=0)
    others = Column(Integer, default=0)


class AddresInfoOrm(BaseModelOrm):
    __tablename__ = "addreses_info"
    record_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=0)
    address = Column(String, default=0)
    lat = Column(Float, default=0.0)
    lon = Column(Float, default=0.0)
    date_time = Column(Integer, default=0)


class UserKpiLevelsOrm(Enum):
    TRAINEE = "Стажер"
    SPECIALIST = "Специалист"
    EXPERT = "Эксперт"
    TOP = "ТОП"


class LastMonthStatisticsWithKpiOrm(BaseModelOrm):
    __tablename__ = "last_month_statistics_with_kpi"
    user_id: Mapped[int] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    flyers = Column(Integer, default=0)
    calls = Column(Integer, default=0)
    shows = Column(Integer, default=0)
    meets = Column(Integer, default=0)
    deals = Column(Integer, default=0)
    deposits = Column(Integer, default=0)
    searches = Column(Integer, default=0)
    analytics = Column(Integer, default=0)
    others = Column(Integer, default=0)
    user_level: Mapped[UserKpiLevelsOrm]
    salary_percentage = Column(Float, default=0.0)


class CallsRecordsOrm(BaseModelOrm):
    __tablename__ = 'calls_records'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    data = Column(LargeBinary)


class UsersCallsOrm(BaseModelOrm):
    __tablename__ = 'users_calls'
    user_id: Mapped[int] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    record_id: Mapped[int] = mapped_column(ForeignKey(CallsRecordsOrm.id, ondelete="CASCADE"), primary_key=True)
    info = Column(String, default="")
    date_time = Column(Integer)
    phone_number = Column(String)
    contact_name = Column(String)
    length_seconds = Column(Integer)
    call_type = Column(Integer)
    transcription = Column(String, default="no transcription")