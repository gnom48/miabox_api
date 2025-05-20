import logging
import aiohttp
import asyncio


class BaseApiService:
    def __init__(self, base_url, https_enable=False):
        self._base_url = "https://" if https_enable else "http://"
        self._base_url += base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        logging.debug("Сессия открыта")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        logging.debug("Сессия закрыта")
