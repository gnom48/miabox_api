from typing import Dict
from fastapi import Header, Request, status
from fastapi.exceptions import HTTPException
import aiohttp
import json
from datetime import datetime

from fastapi.responses import JSONResponse
from app.toml_helper import load_var_from_toml
from app.api import UserCredentials, TokenModel
from dataclasses import asdict, dataclass


async def auth_middleware(request: Request, call_next):
    if not request.url.path.startswith(("/address", "/calls", "/note", "/task", "/team", "/user")):
        return await call_next(request)

    try:
        headers = {'accept': 'application/json'}
        params = {'AccessToken': request.headers['token-authorization']}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://auth:{load_var_from_toml('services', 'auth_port')}/api/Accounts/Me",
                                   headers=headers, params=params) as response:
                response_text = await response.text()
                if not str(response.status).startswith('2'):
                    raise Exception(response_text)

                auth_response = AuthResponse()
                auth_response.from_json(response_text)

                if not auth_response.is_ok:
                    raise Exception()

                request.state.__setattr__(
                    "custom_data", {"user": auth_response.user})
                return await call_next(request)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=e.__str__())


def get_user_from_request(request: Request, token_authorization: str = Header(alias="token-authorization")) -> UserCredentials | None:
    if hasattr(request.state, 'custom_data'):
        return request.state.__getattr__("custom_data")
    return None


@dataclass
class AuthResponse:
    user: UserCredentials
    requested_at: datetime = datetime.now()
    is_ok: bool = False

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        cls.is_ok = True
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(asdict(self))
