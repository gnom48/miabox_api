from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncConnection
from sqlalchemy import text
from .models import *
from core.toml_helper import load_data_from_toml


config = load_data_from_toml()['database']
__CONNRCTION_STR = f"postgresql+asyncpg://{config['postgres_user']}:{config['postgres_password']}@postgres:{config['postgres_port']}/{config['postgres_db']}"

async_engine = create_async_engine(
    __CONNRCTION_STR,
    echo=False,
    pool_size=5,
    max_overflow=3
)
new_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def create_tables():
    async with async_engine.begin() as connection:
        await pre_create_actions(conn=connection)
        await connection.run_sync(BaseModelOrm.metadata.create_all)


async def drop_tables():
    async with async_engine.begin() as connection:
        await pre_delete_actions(conn=connection)
        await connection.run_sync(BaseModelOrm.metadata.drop_all)


async def pre_create_actions(conn: AsyncConnection):
    await conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))


async def pre_delete_actions(conn: AsyncConnection):
    await conn.execute(text("DROP SCHEMA IF EXISTS auth"))
