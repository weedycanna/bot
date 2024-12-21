from typing import Dict

from sqlalchemy import update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product


async def orm_add_product(session: AsyncSession, data: Dict) -> None:
    obj = Product(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"]),
    )
    session.add(obj)
    await session.commit()


async def orm_get_products(session: AsyncSession, category_id=None):
    try:
        if category_id is not None:
            query = select(Product).where(Product.category_id == int(category_id))
        else:
            query = select(Product)

        result = await session.execute(query)
        products = result.scalars().all()
        return products
    except Exception as e:
        print(f"Error in orm_get_products: {e}")
        return []


async def orm_get_product(session: AsyncSession, product_id: int) -> Product:
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalars().first()


async def orm_update_product(
    session: AsyncSession, product_id: int, data: Dict
) -> None:
    query = (
        update(Product)
        .where(Product.id == product_id)
        .values(
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            image=data["image"],
            category_id=int(data["category"]),
        )
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int) -> None:
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()
