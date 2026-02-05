import os
from dotenv import load_dotenv

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.models.car import Car, Base


load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
db_port = os.getenv("POSTGRES_PORT")
postgres_db = os.getenv("POSTGRES_DB")

DATABASE_URL=f"postgresql+asyncpg://{user}:{password}@db:5432/{postgres_db}"

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the .env file")

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_cars_to_db(cars_data: list[dict]):
    if not cars_data:
        return

    async with SessionLocal() as session:
        try:
            stmt = insert(Car).values(cars_data)

            update_attrs = {
                c.name: stmt.excluded[c.name]
                for c in Car.__table__.columns
                if c.name not in ['id', 'url', 'updated_at']
            }

            stmt = stmt.on_conflict_do_update(
                index_elements=['url'],
                set_=update_attrs
            )

            result = await session.execute(stmt)
            await session.commit()


        except Exception as e:
            print(e)
            await session.rollback()