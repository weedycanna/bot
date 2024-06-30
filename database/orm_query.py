import math
from typing import Dict, Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple

from sqlalchemy.orm import joinedload

from database.models import Product, User, Banner, Category, Cart


# Pagination class

class Paginatror:
    def __init__(self, array: List | Tuple, page: int = 1, per_page: int = 1):
        self.array = array
        self.page = page
        self.per_page = per_page
        self.len = len(self.array)

        self.pages = math.ceil(self.len / len.per_page)

    def __get_slice(self):
        start = (self.page - 1) * self.per_page
        stop = start + self.per_page
        return self.array[start:stop]

    def get_page(self):
        page_items = self.__get_slice()
        return page_items

    def has_next(self):
        if self.page < self.pages:
            return self.page + 1
        return False

    def has_previous(self):
        if self.page > 1:
            return self.page - 1
        return False

    def get_next(self):
        if self.page < self.pages:
            self.page += 1
            return self.get_page()
        raise IndexError(f'Next page does not exist. Use has_next() to check if there is a next page')

    def get_previous(self):
        if self.page > 1:
            self.page -= 1
            return self.__get_slice()
        raise IndexError(f'Previous page does not exist. Use has_previous() to check if there is a previous page')


# Banner queries


async def orm_add_banner_description(session: AsyncSession, data: Dict) -> None:
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
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


# Category queries


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


# Admin queries for products


async def orm_add_product(session: AsyncSession, data: Dict) -> None:
    obj = Product(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        image=data['image'],
        category_id=int(data['category']),
    )
    session.add(obj)
    await session.commit()


async def orm_get_products(session: AsyncSession, category_id) -> Sequence[Product]:
    query = select(Product).where(Product.category_id == int(category_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_product(session: AsyncSession, product_id: int) -> Product:
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalars().first()


async def orm_update_product(session: AsyncSession, product_id: int, data: Dict) -> None:
    query = update(Product).where(Product.id == product_id).values(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        image=data['image'],
        category_id=int(data['category'])
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int) -> None:
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()


# User queries


async def orm_add_user(
        session: AsyncSession,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
) -> None:
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
        )
    await session.commit()


# Cart queries


async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int) -> None:
    query = select(Cart).where(
        Cart.user_id == user_id, Cart.product_id == product_id).options(joinedload(Cart.product))
    cart = await session.execute(query)
    cart = cart.scalars().first()
    if cart:
        cart.quantity += 1
        await session.commit()
        return cart
    else:
        session.add(Cart(user_id=user_id, product_id=product_id, quantity=1))
        await session.commit()


async def orm_get_user_carts(session: AsyncSession, user_id: int) -> Sequence[Cart]:
    query = select(Cart).filter(Cart.user_id == user_id).options(joinedload(Cart.product))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int) -> None:
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    await session.execute(query)
    await session.commit()


async def orm_reduce_product_in_cart(session: AsyncSession, user_id: int, product_id: int) -> None:
    query = select(Cart).where(
        Cart.user_id == user_id, Cart.product_id == product_id).options(joinedload(Cart.product))
    cart = await session.execute(query)
    cart = cart.scalars().first()

    if not cart:
        return
    if cart.quantity > 1:
        cart.quantity -= 1
        await session.commit()
        return True
    else:
        await orm_delete_from_cart(session, user_id, product_id)
        await session.commit()
        return False