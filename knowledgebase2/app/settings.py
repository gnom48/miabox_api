from fastapi.templating import Jinja2Templates
from app.redis_client.redis_client import RedisClient
from app.sessions import SessionManager

TEMPLATES_PATH = r"app/templates"
templates = Jinja2Templates(directory=TEMPLATES_PATH)


class Settings:
    session_manager: SessionManager = None
