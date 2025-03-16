from fastapi import Header, Request, status
import aiohttp
import json
from datetime import datetime
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.toml_helper import load_var_from_toml
from app.api.models import UserCredentials
from dataclasses import dataclass, asdict, field


async def auth_middleware(request: Request, call_next):
    if not request.url.path.startswith(("/address", "/calls", "/note", "/task", "/team", "/user", "/files")):
        return await call_next(request)

    try:
        headers = {'accept': 'application/json',
                   'Authorization': request.headers['token-authorization']}
        params = {}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://auth:{load_var_from_toml('services', 'auth_port')}/api/Accounts/Me",
                                   headers=headers, params=params) as response:
                response_text = await response.text()
                if not str(response.status).startswith('2'):
                    raise Exception(response_text)

                auth_response = AuthResponse.model_validate_json(
                    response_text)

                if not auth_response.user.is_active:
                    raise Exception("account is not active")

                request.state.__setattr__(
                    'user_credentials', auth_response.user)
                return await call_next(request)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=e.__str__())


def get_user_from_request(request: Request, token_authorization: str = Header(alias='token-authorization')) -> UserCredentials:
    if hasattr(request.state, 'user_credentials'):
        return request.state.__getattr__('user_credentials')
    return None


class AuthResponse(BaseModel):
    user: UserCredentials
    requested_at: datetime = field(default_factory=datetime.now)
