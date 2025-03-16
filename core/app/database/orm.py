from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncConnection
from sqlalchemy import text
from sqlalchemy.engine.url import URL
from .models import *
from app.toml_helper import load_data_from_toml


config = load_data_from_toml()['database']
# CONNRCTION_STR = f"postgresql+asyncpg://{config['postgres_user']}:{config['postgres_password']}@postgres:{config['postgres_port']}/{config['postgres_db']}"

url = URL.create(
    drivername="postgresql+asyncpg",
    username=config['postgres_user'],
    password=config['postgres_password'],
    host="postgres",
    port=config['postgres_port'],
    database=config['postgres_db']
)


async_engine = create_async_engine(
    # CONNRCTION_STR,
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


async def drop_tables():
    async with async_engine.begin() as connection:
        await connection.run_sync(BaseModelOrm.metadata.drop_all)


async def pre_create_actions(conn: AsyncConnection):
    await conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))


async def after_create_actions(conn: AsyncConnection):
    await conn.execute(text("""   
        DROP TRIGGER IF EXISTS insert_empty_user_info ON auth.user_credentials;
        DROP FUNCTION IF EXISTS insert_empty_user_info();
                            
        CREATE FUNCTION insert_empty_user_info() RETURNS trigger AS $$
            BEGIN
                INSERT INTO public.users(id, "type", email, "name", gender, birthday, phone, image)
                VALUES(NEW.id, 'PRIVATE', '', 'Пользователь', '', 0, '', '1');
                RETURN NULL;
            END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER insert_empty_user_info AFTER INSERT ON auth.user_credentials
            FOR EACH ROW EXECUTE PROCEDURE insert_empty_user_info();
        """))
