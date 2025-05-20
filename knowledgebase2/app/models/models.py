from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class SignInRequest(BaseModel):
    login: str
    password: str


class SignInRespose(BaseModel):
    regular_token: str


class User(BaseModel):
    id: str
    login: str
    privileges: str
    created_at: str
    is_active: bool


class WhoAmIResponse(BaseModel):
    user: User


class UserInfo(BaseModel):
    id: str
    type: str
    email: str | None
    name: str
    gender: str | None
    birthday: int | None
    phone: str | None
    image: str | None


class Member(BaseModel):
    user: UserInfo
    role: str


class Team(BaseModel):
    id: str
    name: str
    created_at: int


class TeamResponse(BaseModel):
    team: Team
    members: List[Member]


class TeamsResponse(BaseModel):
    teams: List[TeamResponse]
