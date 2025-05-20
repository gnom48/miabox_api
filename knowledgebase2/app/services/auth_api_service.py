from .base_api_service import BaseApiService
import logging
from app.toml_helper import load_var_from_toml
from app.models import *


class AuthApiService(BaseApiService):
    """Сервис для HTTP запросов к API Auth"""

    @staticmethod
    def service_factory() -> 'AuthApiService':
        return AuthApiService()

    def __init__(self):
        super().__init__(load_var_from_toml("services", "auth_host") +
                         ":" + load_var_from_toml("services", "auth_port"))

    async def sign_in(self, login: str, password: str) -> str | None:
        """Делает POST запрос на api/Authentication/SignIn"""
        try:
            payload = {
                "login": login,
                "password": password
            }

            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }

            async with self.session as session:
                url = self._base_url + "/api/Authentication/SignIn"
                async with session.post(url, json=payload, headers=headers) as response:
                    response_text = await response.text()
                    if str(response.status).startswith('2'):
                        logging.debug(
                            f"Получен ответ от auth: {response.status}")
                        return SignInRespose.model_validate_json(response_text).regular_token
                    else:
                        raise Exception(
                            f"Error: {response.status} - {response_text}")
        except Exception as e:
            logging.error(f"Получена ошибка от auth: {e.__str__()}")
            return None

    async def who_am_i(self, token: str) -> WhoAmIResponse | None:
        """Делает GET запрос на /api/Accounts/Me"""
        try:
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': token
            }

            async with self.session as session:
                url = self._base_url + "/api/Accounts/Me"
                async with session.get(url, headers=headers) as response:
                    response_text = await response.text()
                    if str(response.status).startswith('2'):
                        logging.debug(
                            f"Получен ответ от auth: {response.status}")
                        return WhoAmIResponse.model_validate_json(response_text)
                    else:
                        raise Exception(
                            f"Error: {response.status} - {response_text}")
        except Exception as e:
            logging.error(f"Получена ошибка от auth: {e.__str__()}")
            return None
