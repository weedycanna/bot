import os

from aiogram.types import FSInputFile, InputMediaPhoto
from django.conf import settings
from fluentogram import TranslatorRunner

from keybords.inline import (
    get_products_btns,
    get_user_cart,
    get_user_catalog_btns,
    get_user_main_btns,
)
from queries.cart_queries import (
    add_to_cart,
    delete_from_cart,
    get_user_carts,
    reduce_product_in_cart,
)
from queries.category_queries import get_categories
from queries.products_queries import get_products
from utils.get_banner_image import get_banner_image
from utils.paginator import Paginator


async def main_menu(level: int, menu_name: str, i18n: TranslatorRunner) -> tuple:
    image = await get_banner_image(menu_name, i18n)
    kbds = get_user_main_btns(level=level, i18n=i18n)
    return image, kbds


async def catalog(level: int, menu_name: str, i18n: TranslatorRunner) -> tuple:
    image = await get_banner_image(menu_name, i18n)
    categories = await get_categories()
    kbds = get_user_catalog_btns(level=level, categories=categories, i18n=i18n)

    return image, kbds


async def pages(paginator: Paginator, i18n: TranslatorRunner) -> dict:
    btns = dict()
    if paginator.has_previous():
        btns[i18n.prev_button()] = "previous"

    if paginator.has_next():
        btns[i18n.next_button()] = "next"

    return btns


async def products(level: int, category: int, page: int, i18n: TranslatorRunner):
    products = await get_products(category_id=category)

    paginator = Paginator(products, page)
    product = paginator.get_page()[0]

    if product.image:
        image = InputMediaPhoto(
            media=FSInputFile(product.image.path),
            caption=i18n.product_details(
                name=product.name,
                description=product.description,
                price=round(product.price, 2),
                current_page=paginator.page,
                total_pages=paginator.pages,
            ),
        )
    else:
        raise ValueError(i18n.product_no_image())

    pagination_btns = await pages(paginator, i18n=i18n)

    kbds = get_products_btns(
        level=level,
        i18n=i18n,
        category=category,
        page=page,
        pagination_btns=pagination_btns,
        product_id=product.id,
    )

    return image, kbds


async def carts(level, menu_name, page, user_id, product_id, i18n: TranslatorRunner):
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
        image = await get_banner_image("cart", i18n)
        kbds = get_user_cart(
            level=level, i18n=i18n, page=None, pagination_btns=None, product_id=None
        )

    else:
        paginator = Paginator(carts, page=page)
        cart = paginator.get_page()[0]

        cart_price = round(cart.quantity * cart.product.price, 2)
        total_price = round(sum(c.quantity * c.product.price for c in carts), 2)

        if cart.product.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(cart.product.image))
            if os.path.exists(image_path):
                image = InputMediaPhoto(
                    media=FSInputFile(image_path),
                    caption=i18n.cart_item_details(
                        name=cart.product.name,
                        price=cart.product.price,
                        quantity=cart.quantity,
                        cart_price=cart_price,
                        current_page=paginator.page,
                        total_pages=paginator.pages,
                        total_price=total_price,
                    ),
                )
            else:
                raise FileNotFoundError(i18n.product_image_not_found(path=image_path))
        else:
            raise ValueError(i18n.product_no_image())

        pagination_btns = await pages(paginator, i18n=i18n)

        kbds = get_user_cart(
            level=level,
            i18n=i18n,
            page=page,
            pagination_btns=pagination_btns,
            product_id=cart.product.id,
        )

    return image, kbds


async def get_menu_content(
    level: int,
    menu_name: str,
    i18n: TranslatorRunner,
    category: int | None = None,
    page: int | None = None,
    product_id: int | None = None,
    user_id: int | None = None,
):
    if level == 0:
        return await main_menu(level, menu_name, i18n=i18n)
    elif level == 1:
        return await catalog(level, menu_name, i18n=i18n)
    elif level == 2:
        return await products(level, category, page, i18n=i18n)
    elif level == 3:
        return await carts(level, menu_name, page, user_id, product_id, i18n=i18n)
