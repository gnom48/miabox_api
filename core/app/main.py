from datetime import datetime
from fastapi import FastAPI, HTTPException, status
# from app.api import router_users, router_notes, router_tasks, router_teams, router_addresses, router_statistics, router_calls
from contextlib import asynccontextmanager

from app.api import get_user_from_request
from app.api import UserCredentials
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import create_tables, drop_tables, Repository
from app.api import auth_middleware
# from apscheduler.triggers.cron import CronTrigger

# main_scheduler = AsyncIOScheduler(timezone="UTC")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # main_scheduler.add_job(func=Repository.clear_day_statistics, trigger=CronTrigger(hour=3-3, minute=0))
    # main_scheduler.add_job(func=Repository.clear_week_statistics, trigger='cron', day_of_week='sun', hour=3-3, minute=5)
    # main_scheduler.add_job(func=Repository.clear_month_statistics, trigger='cron', day='last', hour=3-3, minute=10)
    # main_scheduler.start()
    # print("Планировщики запущены")
    print("Включение")
    # await create_tables()
    yield
    print("Выключение")


app = FastAPI(lifespan=lifespan)

app.middleware("http")(auth_middleware)


@app.get("/config", status_code=status.HTTP_200_OK)
async def server_config_get():
    config = await Repository.get_config()
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database is not availible")
    return {"postgres": config, "datetime": datetime.now()}

# app.include_router(router_teams)
# app.include_router(router_notes)
# app.include_router(router_tasks)
# app.include_router(router_users)
# app.include_router(router_addresses)
# app.include_router(router_statistics)
# app.include_router(router_calls)
