import aiohttp
from fastapi import UploadFile
from .base_api_service import BaseApiService
import logging
from app.toml_helper import load_var_from_toml
from app.models import *


class CoreApiService(BaseApiService):
    """Сервис для HTTP запросов к API Core"""

    @staticmethod
    def service_factory() -> 'CoreApiService':
        return CoreApiService()

    def __init__(self):
        super().__init__(load_var_from_toml("services", "core_host") +
                         ":" + load_var_from_toml("services", "core_port"))

    async def get_my_teams(self, token: str, show_stats: bool = False, show_addresses: bool = False, show_calls: bool = False) -> TeamsResponse | None:
        """Делает GET запрос на /teams/"""
        try:
            headers = {
                'accept': 'application/json',
                'token-authorization': token
            }

            params = {
                'show_stats': int(show_stats),
                'show_addresses': int(show_addresses),
                'show_calls': int(show_calls)
            }

            async with self.session as session:
                url = f"{self._base_url}/teams/"
                async with session.get(url, headers=headers, params=params) as response:
                    response_text = await response.text()
                    # NOTE: самый адекватный способ нормально спарсить
                    response_text = "{" + f"\"teams\":" + response_text + "}"
                    if str(response.status).startswith('2'):
                        logging.debug(
                            f"Получен ответ от core: {response.status}")
                        return TeamsResponse.model_validate_json(response_text)
                    else:
                        raise Exception(
                            f"Error: {response.status} - {response_text}")
        except Exception as e:
            logging.error(f"Получена ошибка от core: {e}")
            return None

    async def upload_file(self, team_id: str, token: str, file: UploadFile) -> str | None:
        """Делает POST запрос на /files/"""
        try:
            headers = {
                'token-authorization': token
            }

            form = aiohttp.FormData()
            form.add_field('file', file.file,
                           filename=file.filename, content_type='text/html')
            form.add_field('file_id', team_id, content_type='text/plain')

            async with self.session as session:
                url = f"{self._base_url}/files/"
                async with session.post(url, headers=headers, data=form) as response:
                    response_text = await response.text()
                    if str(response.status).startswith('2'):
                        logging.debug(
                            f"Получен ответ от core: {response.status}")
                        return response_text
                    else:
                        raise Exception(
                            f"Error: {response.status} - {response_text}")
        except Exception as e:
            logging.error(f"Получена ошибка от core: {e}")
            return None

    async def download_file(self, token: str, file_id: str) -> str | None:
        """Делает GET запрос на /{file_id}/download"""
        try:
            headers = {
                'token-authorization': token
            }

            async with self.session as session:
                url = f"{self._base_url}/files/{file_id}/download"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        logging.debug(
                            f"Получен ответ от core: {response.status}")
                        file_content = await response.read()
                        return file_content.decode('utf-8')
                    else:
                        raise Exception(f"Error: {response.status} - {await response.text()}")
        except Exception as e:
            logging.error(f"Получена ошибка от core: {e}")
            return None

    async def close(self):
        await self.session.close()
