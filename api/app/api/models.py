from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Dict, Optional, Union, Any
from api.app.database.models import TeamOrm, UserOrm


class StatisticPeriods(str, Enum):
    DAY_STATISTICS_PERIOD = "day"
    WEEK_STATISTICS_PERIOD = "week"
    MONTH_STATISTICS_PERIOD = "month"


class UserTypes(str, Enum):
    COMMERCIAL = "Риелтер коммерческой недвижимости"
    PRIVATE = "Риелтер частной недвижимости"


class WorkTasksTypes(str, Enum):
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


class Image(BaseModel):
    id: str
    name: str
    data: bytes


class User(BaseModel):
    id: str
    login: str
    password: str
    type: UserTypes
    email: str
    reg_date: int
    name: str
    gender: Optional[str]
    birthday: Optional[int]
    phone: Optional[str]
    image: Optional[str]


class AuthData(BaseModel):
    login: str
    password: str


class Note(BaseModel):
    id: str
    title: str
    desc: Optional[str]
    date_time: int
    user_id: str
    notification_id: int


class Task(BaseModel):
    id: str
    work_type: WorkTasksTypes
    date_time: int
    desc: Optional[str]
    duration_seconds: int
    user_id: str
    notification_id: int
    is_completed: bool


class Team(BaseModel):
    id: str
    name: str
    created_date_time: datetime


class UserStatuses(str, Enum):
    OWNER = "Владелец"
    USER = "Участник"


class UserTeam(BaseModel):
    team_id: str
    user_id: str
    role: UserStatuses
    
    
class Statistics(BaseModel):
    user_id: str
    data: int


class StatisticsViaOrm(BaseModel):
    user_id: str
    flyers: int
    calls: int
    shows: int
    meets: int
    deals_rent: int
    deals_sale: int
    deposits: int
    searches: int
    analytics: int
    others: int
    regular_contracts: int
    exclusive_contracts: int


class AddresInfo(BaseModel):
    user_id: str
    address: str
    lat: float
    lon: float
    date_time: int


class UserKpiLevels(str, Enum):
    TRAINEE = "Стажер"
    SPECIALIST = "Специалист"
    EXPERT = "Эксперт"
    TOP = "ТОП"


class LastMonthStatisticsWithKpi(BaseModel):
    user_id: str
    flyers: int
    calls: int 
    shows: int 
    meets: int 
    deals_rent: int
    deals_sale: int
    deposits: int 
    searches: int 
    analytics: int 
    others: int 
    regular_contracts: int
    exclusive_contracts: int
    user_level: UserKpiLevels
    salary_percentage: float


class SummaryStatisticsWithLevel(BaseModel):
    user_id: str
    deals_rent: int
    deals_sale: int
    base_percent: float
    user_level: UserKpiLevels


class CallsRecords(BaseModel):
    user_id: str
    name: str
    data: bytes | None


class UsersCalls(BaseModel):
    user_id: str
    record_id: str
    info: str | None
    date_time: int
    phone_number: str
    contact_name: str
    length_seconds: int
    call_type: int
    transcription: str


class UserWithStats:
    def __init__(self, user: UserOrm, statistics: Dict[StatisticPeriods, Union[None, StatisticsViaOrm]], addresses: list[Any], calls: list[Any], role: UserStatuses, kpi: LastMonthStatisticsWithKpi):
        self.user = user
        self.statistics = statistics
        self.addresses = addresses
        self.calls = calls
        self.role = role
        self.kpi = kpi


class TeamWithInfo:
    def __init__(self, team: TeamOrm, members: list[UserWithStats]):
        self.team = team
        self.members = members
