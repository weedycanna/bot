from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Order


async def orm_get_user_orders(session: AsyncSession, user_id: int):
    query = select(Order).where(Order.user_id == user_id).order_by(Order.created.desc())
    result = await session.execute(query)
    return result.scalars().all()