import os

from aiogram.types import FSInputFile, InputMediaPhoto
from django.conf import settings

from keybords.inline import (get_products_btns, get_user_cart,
                             get_user_catalog_btns, get_user_main_btns)
from queries.banner_queries import get_banner
from queries.cart_queries import (add_to_cart, delete_from_cart,
                                  get_user_carts, reduce_product_in_cart)
from queries.category_queries import get_categories
from queries.products_queries import get_products
from utils.paginator import Paginator


async def main_menu(level: int, menu_name: str) -> tuple:

    banner = await get_banner(menu_name)

    if banner and banner.image:
        image_path = os.path.join(settings.MEDIA_ROOT, str(banner.image))
        if os.path.exists(image_path):
            image = InputMediaPhoto(
                media=FSInputFile(image_path), caption=banner.description
            )
        else:
            raise FileNotFoundError(f"Banner image not found: {image_path}")
    else:
        raise ValueError("Banner not found or has no image")

    kbds = get_user_main_btns(level=level)
    return image, kbds


async def catalog(level: int, menu_name: str) -> tuple:

    banner = await get_banner(menu_name)

    if banner and banner.image:
        image_path = os.path.join(settings.MEDIA_ROOT, str(banner.image))
        if os.path.exists(image_path):
            image = InputMediaPhoto(
                media=FSInputFile(image_path), caption=banner.description
            )
        else:
            raise FileNotFoundError(f"Banner image not found: {image_path}")
    else:
        raise ValueError("Banner not found or has no image")

    categories = await get_categories()
    kbds = get_user_catalog_btns(level=level, categories=categories)

    return image, kbds


async def pages(paginator: Paginator) -> dict:
    btns = dict()
    if paginator.has_previous():
        btns["◀ Prev"] = "previous"

    if paginator.has_next():
        btns["Next ▶"] = "next"

    return btns


async def products(level: int, category: int, page: int):
    products = await get_products(category_id=category)

    paginator = Paginator(products, page)
    product = paginator.get_page()[0]

    if product.image:
        image = InputMediaPhoto(
            media=FSInputFile(product.image.path),
            caption=f"<strong>{product.name}\
                </strong>\n{product.description}\nPrice: {round(product.price, 2)}\n\
                <strong>Good {paginator.page} of {paginator.pages}</strong>",
        )
    else:
        raise ValueError("Product has no image")

    pagination_btns = await pages(paginator)

    kbds = get_products_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=pagination_btns,
        product_id=product.id,
    )

    return image, kbds


async def carts(level, menu_name, page, user_id, product_id):
    if menu_name == "delete":
        await delete_from_cart(user_id, product_id)
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await reduce_product_in_cart(user_id, product_id)
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await add_to_cart(user_id, product_id)

    carts = await get_user_carts(user_id)

    if not carts:
        banner = await get_banner("cart")
        if banner and banner.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(banner.image))
            if os.path.exists(image_path):
                image = InputMediaPhoto(
                    media=FSInputFile(image_path),
                    caption=f"<strong>{banner.description}</strong>",
                )
            else:
                raise FileNotFoundError(f"Banner image not found: {image_path}")
        else:
            raise ValueError("Banner not found or has no image")

        kbds = get_user_cart(
            level=level,
            page=None,
            pagination_btns=None,
            product_id=None,
        )

    else:
        paginator = Paginator(carts, page=page)
        cart = paginator.get_page()[0]

        cart_price = round(cart.quantity * cart.product.price, 2)
        total_price = round(
            sum(cart.quantity * cart.product.price for cart in carts), 2
        )

        if cart.product.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(cart.product.image))
            if os.path.exists(image_path):
                image = InputMediaPhoto(
                    media=FSInputFile(image_path),
                    caption=f"<strong>{cart.product.name}</strong>\n{cart.product.price}$ x {cart.quantity} = {cart_price}$\
                            \nGood {paginator.page} из {paginator.pages} in cart.\nTotal price in cart {total_price}",
                )
            else:
                raise FileNotFoundError(f"Product image not found: {image_path}")
        else:
            raise ValueError("Product has no image")

        pagination_btns = await pages(paginator)

        kbds = get_user_cart(
            level=level,
            page=page,
            pagination_btns=pagination_btns,
            product_id=cart.product.id,
        )

    return image, kbds


async def get_menu_content(
    level: int,
    menu_name: str,
    category: int | None = None,
    page: int | None = None,
    product_id: int | None = None,
    user_id: int | None = None,
):

    if level == 0:
        return await main_menu(level, menu_name)
    elif level == 1:
        return await catalog(level, menu_name)
    elif level == 2:
        return await products(level, category, page)
    elif level == 3:
        return await carts(level, menu_name, page, user_id, product_id)
