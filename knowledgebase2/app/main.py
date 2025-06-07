from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.models import *
from app.settings import Settings
from app.routers import auth_router, main_router
from app.redis_client.redis_client import RedisClient
from app.sessions import SessionManager


app = FastAPI(title='Knowledgebase')

# app.add_middleware(SessionMiddleware,
#                    secret_key=load_var_from_toml("access", "secret_key"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # global session_manager
    Settings.session_manager = SessionManager(RedisClient.factory())
    yield
    # await session_manager.cleanup_expired_sessions()
    # del session_manager

app.router.lifespan_context = lifespan
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router)
app.include_router(main_router)
