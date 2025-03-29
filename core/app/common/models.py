from pydantic import BaseModel
from typing import List, Optional, Dict
from app.api.models import *


class UserWithRole(BaseModel):
    user: User
    stats: Dict[WorkTypes | str, int] = {}
    addresses: List[Address] = []
    calls: List[Call] = []
    kpi: Kpi = None
    role: UserStatuses | str


class TeamWithInfo(BaseModel):
    team: Team
    members: List[UserWithRole]
