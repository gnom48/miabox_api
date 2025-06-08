import asyncio
from datetime import datetime
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, RedirectResponse
from contextlib import asynccontextmanager
from app.database import create_tables, drop_tables, BaseRepository
from app.api import auth_middleware, error_middleware, router_files, router_users, router_addresses, router_calls, router_notes, router_tasks, router_teams, router_statistics
from app.utils.rabbitmq import listen
from app.toml_helper import load_var_from_toml


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging._nameToLevel[str(
        load_var_from_toml("app", "log_level")).upper()])
    logging.debug("Сервер запущен")
    # await drop_tables()
    # await create_tables()
    # logging.debug("Таблицы БД сброшены")
    listen_task = asyncio.create_task(listen())
    logging.debug("Слушатель сообщений запущен")

    yield
    listen_task.cancel()
    try:
        await listen_task
    except asyncio.CancelledError:
        logging.debug("Слушатель сообщений остановлен")

    logging.debug("Сервер выключен")


app = FastAPI(lifespan=lifespan,
              openapi_url="/core/core/openapi.json",
              docs_url="/swagger"
              )

app.middleware("http")(error_middleware)
app.middleware("http")(auth_middleware)


@app.get("/", include_in_schema=False)
async def redirect_to_swagger():
    return RedirectResponse("/swagger")


@app.get("/core/openapi.json", include_in_schema=False)
async def get_swagger():
    # REVIEW:
    return FileResponse(r'/core/app/api/docs/openapi.json')


@app.get("/config", status_code=status.HTTP_200_OK)
async def server_config_get():
    config = await BaseRepository.get_config()
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database is not availible")
    return {"postgres": config, "datetime": datetime.now()}


@app.get("/supported_versions", status_code=status.HTTP_200_OK)
async def get_supported_versions():
    return await BaseRepository.get_supported_versions()

app.include_router(router_files)
app.include_router(router_teams)
app.include_router(router_notes)
app.include_router(router_tasks)
app.include_router(router_users)
app.include_router(router_addresses)
app.include_router(router_statistics)
app.include_router(router_calls)
