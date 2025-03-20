from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from uuid import UUID


class AuthPrivileges(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserTypes(str, Enum):
    COMMERCIAL = "COMMERCIAL"
    PRIVATE = "PRIVATE"


class WorkTypes(str, Enum):
    FLYERS = "FLYERS"
    CALLS = "CALLS"
    SHOW = "SHOW"
    MEET = "MEET"
    DEAL_RENT = "DEAL_RENT"
    DEAL_SALE = "DEAL_SALE"
    DEPOSIT = "DEPOSIT"
    SEARCH = "SEARCH"
    ANALYTICS = "ANALYTICS"
    OTHER = "OTHER"
    REGULAR_CONTRACT = "REGULAR_CONTRACT"
    EXCLUSIVE_CONTRACT = "EXCLUSIVE_CONTRACT"


class KpiLevels(str, Enum):
    TRAINEE = "TRAINEE"
    SPECIALIST = "SPECIALIST"
    EXPERT = "EXPERT"
    TOP = "TOP"


class StatisticPeriod(str, Enum):
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"


class UserStatuses(str, Enum):
    OWNER = "OWNER"
    USER = "USER"


class FileAccessMode(str, Enum):
    READ = "READ"
    WRITE = "WRITE"


class UserCredentials(BaseModel):
    id: str
    login: str
    password: str = ""
    privileges: AuthPrivileges | str
    created_at: datetime
    is_active: bool


class Version(BaseModel):
    suported_versions: List[str]


class Token(BaseModel):
    id: str
    user_id: str
    token: str
    is_regular: bool


class File(BaseModel):
    id: str
    obj_name: str
    bucket_name: str


class User(BaseModel):
    id: str
    type: UserTypes | str
    email: str
    name: str
    gender: Optional[str]
    birthday: Optional[int]
    phone: Optional[str]
    image: Optional[str]


class AuthData(BaseModel):
    login: str
    password: str


class RegData(BaseModel):
    auth_data: AuthData
    user_info: User


class Note(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    created_at: int


class Task(BaseModel):
    id: str
    user_id: str
    work_type: WorkTypes | str
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
    role: UserStatuses | str


class FilesAccess(BaseModel):
    id: str
    user_id: str
    file_id: str
    file_access_mode: FileAccessMode | str


class Statistic(BaseModel):
    id: str
    user_id: str
    period_type: StatisticPeriod | str
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
    user_level: KpiLevels | str
    salary_percentage: float


class Call(BaseModel):
    id: str
    user_id: str
    date_time: int
    phone_number: str
    contact_name: str
    length_seconds: int
    call_type: int
    transcription: Optional[str]
    file_id: Optional[str]


@dataclass
class TokenModel:
    user_id: UUID
    exp: float
    jti: UUID
    iat: float
    sub: str

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            user_id=UUID(json_data["user_id"]),
            exp=json_data["exp"],
            jti=UUID(json_data["jti"]),
            iat=json_data["iat"],
            sub=json_data["sub"]
        )
