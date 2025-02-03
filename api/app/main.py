from fastapi import FastAPI
# from .api import router_users, router_notes, router_tasks, router_teams, router_addresses, router_statistics, router_calls
from contextlib import asynccontextmanager
# from .repository import Repository
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .database import create_tables, drop_tables
# from apscheduler.triggers.cron import CronTrigger

# main_scheduler = AsyncIOScheduler(timezone="UTC")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # main_scheduler.add_job(func=Repository.clear_day_statistics, trigger=CronTrigger(hour=3-3, minute=0))
    # main_scheduler.add_job(func=Repository.clear_week_statistics, trigger='cron', day_of_week='sun', hour=3-3, minute=5)
    # main_scheduler.add_job(func=Repository.clear_month_statistics, trigger='cron', day='last', hour=3-3, minute=10)
    # main_scheduler.start()
    # print("Планировщики запущены")
    # await create_tables()
    yield
    print("Выключение")


app = FastAPI(lifespan=lifespan)
# app.include_router(router_teams)
# app.include_router(router_notes)
# app.include_router(router_tasks)
# app.include_router(router_users)
# app.include_router(router_addresses)
# app.include_router(router_statistics)
# app.include_router(router_calls)
