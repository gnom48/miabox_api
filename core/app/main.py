from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from app.database import create_tables, drop_tables, BaseRepository
from app.api import auth_middleware, error_middleware, router_files, router_users, router_addresses, router_calls, router_notes, router_tasks, router_teams
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.cron import CronTrigger

# main_scheduler = AsyncIOScheduler(timezone="UTC")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # main_scheduler.add_job(func=Repository.clear_day_statistics, trigger=CronTrigger(hour=3-3, minute=0))
    # main_scheduler.add_job(func=Repository.clear_week_statistics, trigger='cron', day_of_week='sun', hour=3-3, minute=5)
    # main_scheduler.add_job(func=Repository.clear_month_statistics, trigger='cron', day='last', hour=3-3, minute=10)
    # main_scheduler.start()
    # print("Планировщики запущены")
    print("Сервер запущен")
    # await drop_tables()
    # await create_tables()
    yield
    print("Сервер выключен")


app = FastAPI(lifespan=lifespan,
              openapi_url="/openapi.json",
              docs_url="/swagger"
              )

app.middleware("http")(error_middleware)
app.middleware("http")(auth_middleware)


@app.get("/", include_in_schema=False)
async def redirect_to_swagger():
    return RedirectResponse("/swagger")


@app.get("/config", status_code=status.HTTP_200_OK)
async def server_config_get():
    config = await BaseRepository.get_config()
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database is not availible")
    return {"postgres": config, "datetime": datetime.now()}

# TODO: создать таблицуи проверить


@app.get("/supported_versions", status_code=status.HTTP_200_OK)
async def get_supported_versions():
    return await BaseRepository.get_supported_versions()

app.include_router(router_files)
app.include_router(router_teams)
app.include_router(router_notes)
app.include_router(router_tasks)
app.include_router(router_users)
app.include_router(router_addresses)
# app.include_router(router_statistics)
app.include_router(router_calls)
