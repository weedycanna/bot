from typing import Sequence, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Category


async def orm_get_categories(session: AsyncSession) -> Sequence:
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_create_categories(session: AsyncSession, categories: List[str]) -> None:
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories])
    await session.commit()