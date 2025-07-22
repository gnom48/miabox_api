from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncConnection
from sqlalchemy import text
from sqlalchemy.engine.url import URL
from app.database.models import *
from app.toml_helper import load_data_from_toml


config = load_data_from_toml()['database']
url = URL.create(
    drivername="postgresql+asyncpg",
    username=config['postgres_user'],
    password=config['postgres_password'],
    host=config['postgres_host'],
    port=int(config['postgres_port']),
    database=config['postgres_db']
)


async_engine = create_async_engine(
    url,
    echo=False,
    pool_size=5,
    max_overflow=3
)
new_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def create_tables():
    async with async_engine.begin() as connection:
        await pre_create_actions(conn=connection)
        await connection.run_sync(BaseModelOrm.metadata.create_all)
        await after_create_actions(conn=connection)


async def drop_tables():
    async with async_engine.begin() as connection:
        await connection.run_sync(BaseModelOrm.metadata.drop_all)


async def pre_create_actions(conn: AsyncConnection):
    await conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))


async def after_create_actions(conn: AsyncConnection):
    ...
    # DEPRECATED:
    # commands = [
    #     "DROP TRIGGER IF EXISTS insert_empty_user_info ON auth.user_credentials;",
    #     "DROP FUNCTION IF EXISTS insert_empty_user_info();",
    #     """
    #     CREATE FUNCTION insert_empty_user_info() RETURNS trigger AS $$
    #     BEGIN
    #         INSERT INTO public.users(id, "type", email, "name", gender, birthday, phone, image)
    #         VALUES(NEW.id, 'PRIVATE', '', 'Пользователь', '', 0, '', null);
    #         RETURN NULL;
    #     END;
    #     $$ LANGUAGE plpgsql;
    #     """,
    #     """
    #     CREATE TRIGGER insert_empty_user_info
    #     AFTER INSERT ON auth.user_credentials
    #     FOR EACH ROW EXECUTE PROCEDURE insert_empty_user_info();
    #     """
    # ]

    # for command in commands:
    #     await conn.execute(text(command))
