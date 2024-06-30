import os

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from common.texts_for_db import categories, description_for_info_pages

from database.models import Base
from database.orm_query import orm_create_categories, orm_add_banner_description

engine = create_async_engine(os.getenv('DB_PG'), echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=True)


async def create_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await orm_create_categories(session, categories)
        await orm_add_banner_description(session, description_for_info_pages)


async def drop_db() -> Base:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)