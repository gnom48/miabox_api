from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .consts import CONNRCTION_STR
from .models import *


async_engine = create_async_engine(CONNRCTION_STR, echo=False, pool_size=5, max_overflow=10)

new_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def create_tables():
    async with async_engine.begin() as connection:
        await connection.run_sync(BaseModelOrm.metadata.create_all)
        
async def drop_tables():
    async with async_engine.begin() as connection:
        await connection.run_sync(BaseModelOrm.metadata.drop_all)