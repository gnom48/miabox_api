from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, Column, Integer, LargeBinary, String, Float, Boolean
from enum import Enum
import uuid


class BaseModelOrm(DeclarativeBase):
    pass


class UserTypesOrm(Enum):
    COMMERCIAL = "Риелтор коммерческой недвижимости"
    PRIVATE = "Риелтор частной недвижимости"
    
    
class WorkTasksTypesOrm(Enum):
    FLYERS = "Рассклейка"
    CALLS = "Обзвон"
    SHOW = "Показ объекта"
    MEET = "Встреча по объекту"
    DEAL_RENT = "Сделка по аренде"
    DEAL_SALE = "Сделка по продаже"
    DEPOSIT = "Получение задатка"
    SEARCH = "Поиск объектов"
    ANALYTICS = "Аналитика рынка"
    OTHER = "Нечто особенное"
    REGULAR_CONTRACT = "Обычный договор"
    EXCLUSIVE_CONTRACT = "Эксклюзивный договор"


class ImageOrm(BaseModelOrm):
    __tablename__ = 'images'
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    data = Column(LargeBinary, nullable=True)


class UserOrm(BaseModelOrm):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    login = Column(String, unique=True)
    password: Mapped[str]
    type: Mapped[UserTypesOrm]
    email: Mapped[str]
    reg_date: Mapped[int]
    name = Column(String, default="Пользователь")
    gender: Mapped[str | None]
    birthday: Mapped[int | None]
    phone: Mapped[str | None]
    image: Mapped[str] = mapped_column(ForeignKey(ImageOrm.id), default="1")


class NoteOrm(BaseModelOrm):
    __tablename__ = "notes"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str]
    desc: Mapped[str | None]
    date_time: Mapped[int]
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"))
    notification_id: Mapped[int]


class TaskOrm(BaseModelOrm):
    __tablename__ = "tasks"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    work_type: Mapped[WorkTasksTypesOrm]
    desc: Mapped[str | None]
    date_time: Mapped[int]
    duration_seconds: Mapped[int]
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"))
    notification_id: Mapped[int]
    is_completed = Column(Boolean, default=False)
    

class TeamOrm(BaseModelOrm):
    __tablename__ = "teams"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str]
    created_date_time = Mapped[int]
    

class UserStatusesOrm(Enum):
    OWNER = "Владелец"
    USER = "Участник"
    
    
class UserTeamOrm(BaseModelOrm):
    __tablename__ = "user_teams"
    team_id: Mapped[str] = mapped_column(ForeignKey(TeamOrm.id, ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    role: Mapped[UserStatusesOrm]


class DayStatisticsOrm(BaseModelOrm):
    __tablename__ = "day_statistics"
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    flyers = Column(Integer, default=0)
    calls = Column(Integer, default=0)
    shows = Column(Integer, default=0)
    meets = Column(Integer, default=0)
    deals_rent = Column(Integer, default=0)
    deals_sale = Column(Integer, default=0)
    deposits = Column(Integer, default=0)
    searches = Column(Integer, default=0)
    analytics = Column(Integer, default=0)
    others = Column(Integer, default=0)
    regular_contracts = Column(Integer, default=0)
    exclusive_contracts = Column(Integer, default=0)


class WeekStatisticsOrm(BaseModelOrm):
    __tablename__ = "week_statistics"
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    flyers = Column(Integer, default=0)
    calls = Column(Integer, default=0)
    shows = Column(Integer, default=0)
    meets = Column(Integer, default=0)
    deals_rent = Column(Integer, default=0)
    deals_sale = Column(Integer, default=0)
    deposits = Column(Integer, default=0)
    searches = Column(Integer, default=0)
    analytics = Column(Integer, default=0)
    others = Column(Integer, default=0)
    regular_contracts = Column(Integer, default=0)
    exclusive_contracts = Column(Integer, default=0)


class MonthStatisticsOrm(BaseModelOrm):
    __tablename__ = "month_statistics"
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    flyers = Column(Integer, default=0)
    calls = Column(Integer, default=0)
    shows = Column(Integer, default=0)
    meets = Column(Integer, default=0)
    deals_rent = Column(Integer, default=0)
    deals_sale = Column(Integer, default=0)
    deposits = Column(Integer, default=0)
    searches = Column(Integer, default=0)
    analytics = Column(Integer, default=0)
    others = Column(Integer, default=0)
    regular_contracts = Column(Integer, default=0)
    exclusive_contracts = Column(Integer, default=0)


class AddresInfoOrm(BaseModelOrm):
    __tablename__ = "addreses_info"
    record_id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    address = Column(String, default="")
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
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    flyers = Column(Integer, default=0)
    calls = Column(Integer, default=0)
    shows = Column(Integer, default=0)
    meets = Column(Integer, default=0)
    deals_rent = Column(Integer, default=0)
    deals_sale = Column(Integer, default=0)
    deposits = Column(Integer, default=0)
    searches = Column(Integer, default=0)
    analytics = Column(Integer, default=0)
    others = Column(Integer, default=0)
    regular_contracts = Column(Integer, default=0)
    exclusive_contracts = Column(Integer, default=0)
    user_level: Mapped[UserKpiLevelsOrm]
    salary_percentage = Column(Float, default=0.0)


class SummaryStatisticsWithLevelOrm(BaseModelOrm):
    __tablename__ = "summary_statistics_with_level"
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    deals_rent = Column(Integer, default=0)
    deals_sale = Column(Integer, default=0)
    base_percent = Column(Float, default=0)
    user_level: Mapped[UserKpiLevelsOrm]


class CallsRecordsOrm(BaseModelOrm):
    __tablename__ = 'calls_records'
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    data = Column(LargeBinary, nullable=True)


class UsersCallsOrm(BaseModelOrm):
    __tablename__ = 'users_calls'
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id, ondelete="CASCADE"), primary_key=True)
    record_id: Mapped[str] = mapped_column(ForeignKey(CallsRecordsOrm.id, ondelete="CASCADE"), primary_key=True)
    info = Column(String, default="")
    date_time = Column(Integer)
    phone_number = Column(String)
    contact_name = Column(String)
    length_seconds = Column(Integer)
    call_type = Column(Integer)
    transcription = Column(String, default="no transcription")