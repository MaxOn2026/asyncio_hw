import asyncio

from sqlalchemy import inspect
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_URL = "sqlite+aiosqlite:///star_wars.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    birth_year: Mapped[str | None] = mapped_column(nullable=True)
    eye_color: Mapped[str | None] = mapped_column(nullable=True)
    gender: Mapped[str | None] = mapped_column(nullable=True)
    hair_color: Mapped[str | None] = mapped_column(nullable=True)
    homeworld: Mapped[str | None] = mapped_column(nullable=True)
    mass: Mapped[str | None] = mapped_column(nullable=True)
    skin_color: Mapped[str | None] = mapped_column(nullable=True)

async def write_characters(records: tuple[dict]):
    if not records:
        return None

    async with async_session_factory() as session:
        mapper = inspect(Character)
        valid_keys = {attr.key for attr in mapper.attrs}
        for record in records:
            if not record:
                continue
            result = record.get("result") or {}
            props = result.get("properties") or {}
            filtered = {k: v for k, v in props.items() if k in valid_keys}
            filtered.pop("id", None)
            if not filtered:
                continue

            stmt = insert(Character).values(**filtered).on_conflict_do_nothing()
            await session.execute(stmt)
        await session.commit()
        return True

async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        # Создаём все таблицы
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("db and tables initialized successfully")

if __name__ == "__main__":
    asyncio.run(init_db())