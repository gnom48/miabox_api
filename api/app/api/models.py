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
    DEAL = "Сделка"
    DEPOSIT = "Получение задатка"
    SEARCH = "Поиск объектов"
    ANALYTICS = "Аналитика рынка"
    OTHER = "Нечто особенное"


class Image(BaseModel):
    id: int
    name: str
    data: bytes


class User(BaseModel):
    id: int
    login: str
    password: str
    type: UserTypes
    email: str
    reg_date: int
    name: str
    gender: Optional[str]
    birthday: Optional[int]
    phone: Optional[str]
    image: Optional[int]
    
    
class UserTmp(BaseModel):
    id: int
    login: str
    password: str
    type: UserTypes
    photo: str
    reg_date: int
    name: str
    gender: Optional[str]
    birthday: Optional[int]
    phone: Optional[str]


class Note(BaseModel):
    id: int
    title: str
    desc: Optional[str]
    date_time: int
    user_id: int
    notification_id: int


class Task(BaseModel):
    id: int
    work_type: WorkTasksTypes
    date_time: int
    desc: Optional[str]
    duration_seconds: int
    user_id: int
    notification_id: int


class Team(BaseModel):
    id: int
    name: str
    created_date_time: datetime


class UserStatuses(str, Enum):
    OWNER = "Владелец"
    USER = "Участник"


class UserTeam(BaseModel):
    team_id: int
    user_id: int
    role: UserStatuses
    
    
class Statistics(BaseModel):
    user_id: int
    data: int


class StatisticsOrm(BaseModel):
    user_id: int
    flyers: int
    calls: int
    shows: int
    meets: int
    deals: int
    deposits: int
    searches: int
    analytics: int
    others: int


class AddresInfo(BaseModel):
    user_id: int
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
    user_id: int
    flyers: int
    calls: int 
    shows: int 
    meets: int 
    deals: int 
    deposits: int 
    searches: int 
    analytics: int 
    others: int 
    user_level: UserKpiLevels
    salary_percentage: float


class SummaryStatisticsWithLevel(BaseModel):
    user_id: int
    deals: int
    base_percent: int
    user_level: UserKpiLevels


class CallsRecords(BaseModel):
    id: int
    name: str
    data: bytes


class UsersCalls(BaseModel):
    user_id: int
    record_id: int
    info: str | None
    date_time: int
    phone_number: str
    contact_name: str
    length_seconds: int
    call_type: int
    transcription: str


class UserWithStats:
    def __init__(self, user: UserOrm, statistics: Dict[StatisticPeriods, Union[None, StatisticsOrm]], addresses: list[Any], calls: list[Any], role: UserStatuses, kpi: LastMonthStatisticsWithKpi):
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
