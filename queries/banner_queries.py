from typing import Dict, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Banner
from sqlalchemy import select, update


async def orm_add_banner_description(session: AsyncSession, data: Dict) -> None:
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all(
        [
            Banner(name=name, description=description)
            for name, description in data.items()
        ]
    )
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str) -> None:
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str) -> Banner:
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalars().first()


async def orm_get_info_pages(session: AsyncSession) -> Sequence[Banner]:
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()