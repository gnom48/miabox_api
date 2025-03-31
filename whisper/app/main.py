import asyncio
from .transcription import AsyncWhisper, Models
from contextlib import asynccontextmanager
import logging
from .rabbitmq import listen
from minio_client import MinioClient
from .toml_helper import load_var_from_toml


@asynccontextmanager
async def lifespan():
    logging.debug("Старт")

    minio_client = MinioClient(
        f"{load_var_from_toml("minio", "minio_api_host")}:{load_var_from_toml("minio", "minio_api_port")}",
        load_var_from_toml("minio", "minio_access_key"),
        load_var_from_toml("minio", "minio_secret_key")
    )
    logging.debug("Minio клиент готов")

    async_whisper_model = AsyncWhisper()
    await async_whisper_model.initialize_async(load_var_from_toml("app", "model"))
    logging.debug("Модель готова")

    await listen(minio_client=minio_client, async_whisper_model=async_whisper_model)
    logging.debug("Слушатель сообщений запущен")

    yield

    logging.debug("Выключение")


async def main():
    async with lifespan() as _:
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
