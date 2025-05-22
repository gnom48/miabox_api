import logging
from redis.asyncio import Redis
from app.toml_helper import load_data_from_toml


class RedisClient:
    def __init__(self, host: str, port: int, db: int = 0):
        self.host: str = host
        self.port: int = port
        self.db: int = db
        self.__redis_conn: Redis = None

        self.connect()

    def connect(self):
        """Устанавливаем соединение с Redis"""
        if not self.__redis_conn:
            self.__redis_conn = Redis(
                host=self.host, port=self.port, db=self.db)

    async def close(self):
        """Закрываем соединение с Redis"""
        if self.__redis_conn:
            await self.__redis_conn.close()
            del self.__redis_conn

    async def ping(self):
        """Проверяет связь с Redis"""
        self.connect()
        return await self.__redis_conn.ping() == True

    async def set(self, key, value):
        """Устаналивает ключ-значение в Redis"""
        self.connect()
        await self.__redis_conn.set(key, value)

    async def get(self, key):
        """Получает значение ключа из Redis"""
        self.connect()
        result = await self.__redis_conn.get(key)
        return result.decode('utf-8') if isinstance(result, bytes) else result

    async def delete(self, key):
        """Удаляет ключ из Redis"""
        self.connect()
        await self.__redis_conn.delete(key)

    @classmethod
    def factory(cls):
        """Возвращает экземпляр RedisClient с настроенными параметрами из TOML-конфигурации"""
        config = load_data_from_toml()["services"]
        instance = cls(config["redis_host"], int(
            config["redis_port"]))
        instance.connect()
        return instance
