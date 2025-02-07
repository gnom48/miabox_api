from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class AuthPrivileges(str, Enum):
    USER = "Пользователь"
    ADMIN = "Администратор"

class UserTypes(str, Enum):
    COMMERCIAL = "Риелтор коммерческой недвижимости"
    PRIVATE = "Риелтор частной недвижимости"

class WorkTypes(str, Enum):
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

class KpiLevels(str, Enum):
    TRAINEE = "Стажер"
    SPECIALIST = "Специалист"
    EXPERT = "Эксперт"
    TOP = "ТОП"

class StatisticPeriod(str, Enum):
    DAY = "День"
    WEEK = "Неделя"
    MONTH = "Месяц"

class UserStatuses(str, Enum):
    OWNER = "Владелец"
    USER = "Участник"

class UserCredentials(BaseModel):
    id: str
    login: str
    password: str
    privileges: AuthPrivileges
    created_at: datetime
    is_active: bool

class Token(BaseModel):
    id: str
    user_id: str
    token: str
    is_regular: bool

class File(BaseModel):
    id: str
    obj_key: str
    obj_name: str
    bucket_name: str

class User(BaseModel):
    id: str
    type: UserTypes
    email: str
    name: str
    gender: Optional[str]
    birthday: Optional[int]
    phone: Optional[str]
    image: str

class Note(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    created_at: int

class Task(BaseModel):
    id: str
    user_id: str
    work_type: WorkTypes
    description: Optional[str]
    created_at: int
    duration_seconds: int
    is_completed: bool

class Team(BaseModel):
    id: str
    name: str
    created_at: int

class UserTeam(BaseModel):
    team_id: str
    user_id: str
    role: UserStatuses

class Statistic(BaseModel):
    id: str
    user_id: str
    period_type: StatisticPeriod
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

class Address(BaseModel):
    id: str
    user_id: str
    address: str
    lat: float
    lon: float
    date_time: int

class Kpi(BaseModel):
    user_id: str
    user_level: KpiLevels
    salary_percentage: float

class Call(BaseModel):
    id: str
    user_id: str
    date_time: int
    phone_number: str
    contact_name: str
    length_seconds: int
    call_type: int
    transcription: str
    file_id: str
