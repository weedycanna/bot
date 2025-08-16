from typing import Dict, List, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner
from parler.utils.context import switch_language

from callbacks.callbacks import (LanguageCallBack, MenuCallBack,
                                 OrderDetailCallBack)
from django_project.telegrambot.usersmanage.models import Category


def get_user_main_btns(*, level: int, i18n: TranslatorRunner, sizes: Tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        i18n.main_menu_goods(): "catalog",
        i18n.main_menu_cart(): "cart",
        i18n.main_menu_orders(): "orders",
        i18n.main_menu_about(): "about",
        i18n.main_menu_payment(): "payment",
        i18n.main_menu_delivery(): "shipping",
        i18n.main_menu_profile(): "profile",
        i18n.main_menu_language(): "language",
    }

    for text, menu_name in btns.items():
        if menu_name == "catalog":
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level + 1, menu_name=menu_name
                    ).pack(),
                )
            )
        elif menu_name == "cart":
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(level=3, menu_name=menu_name).pack(),
                )
            )
        elif menu_name == "orders":
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(level=level, menu_name=menu_name).pack(),
                )
            )
        elif menu_name == "profile":
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(level=level, menu_name=menu_name).pack(),
                )
            )
        elif menu_name == "language":
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(level=level, menu_name=menu_name).pack(),
                )
            )
        else:
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(level=level, menu_name=menu_name).pack(),
                )
            )

    return keyboard.adjust(*sizes).as_markup()


def get_user_cart(
    *,
    i18n: TranslatorRunner,
    level: int,
    page: int | None,
    pagination_btns: dict | None,
    product_id: int | None,
    sizes: tuple[int] = (3,),
):
    keyboard = InlineKeyboardBuilder()
    if page:
        keyboard.add(
            InlineKeyboardButton(
                text=i18n.delete_button(),
                callback_data=MenuCallBack(
                    level=level, menu_name="delete", product_id=product_id, page=page
                ).pack(),
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text="-1",
                callback_data=MenuCallBack(
                    level=level, menu_name="decrement", product_id=product_id, page=page
                ).pack(),
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text="+1",
                callback_data=MenuCallBack(
                    level=level, menu_name="increment", product_id=product_id, page=page
                ).pack(),
            )
        )

        keyboard.adjust(*sizes)

        row = []

        for text, menu_name in pagination_btns.items():
            if menu_name == "next":
                row.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=MenuCallBack(
                            level=level, menu_name=menu_name, page=page + 1
                        ).pack(),
                    )
                )
            elif menu_name == "previous":
                row.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=MenuCallBack(
                            level=level, menu_name=menu_name, page=page - 1
                        ).pack(),
                    )
                )

        keyboard.row(*row)

        row2 = [
            InlineKeyboardButton(
                text=i18n.main_menu_button(),
                callback_data=MenuCallBack(level=0, menu_name="main").pack(),
            ),
            InlineKeyboardButton(
                text=i18n.order_button(),
                callback_data=MenuCallBack(level=0, menu_name="order").pack(),
            ),
        ]
        return keyboard.row(*row2).as_markup()
    else:
        keyboard.add(
            InlineKeyboardButton(
                text=i18n.main_menu_button(),
                callback_data=MenuCallBack(level=0, menu_name="main").pack(),
            )
        )

        return keyboard.adjust(*sizes).as_markup()


def get_user_catalog_btns(
    *,
    i18n: TranslatorRunner,
    level: int,
    user_language: str,
    categories: List[Category],
    sizes: Tuple[int] = (2,),
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(
            text=i18n.back_button(),
            callback_data=MenuCallBack(level=level - 1, menu_name="main").pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=i18n.cart_button(),
            callback_data=MenuCallBack(level=3, menu_name="cart").pack(),
        )
    )
    for c in categories:
        with switch_language(c, user_language):
            keyboard.add(
                InlineKeyboardButton(
                    text=c.name,
                    callback_data=MenuCallBack(
                        level=level + 1, menu_name=c.name, category=c.id
                    ).pack(),
                )
            )

    return keyboard.adjust(*sizes).as_markup()


def get_products_btns(
    *,
    i18n: TranslatorRunner,
    level: int,
    category: int,
    page: int,
    user_language: str,
    pagination_btns: dict,
    product_id: int,
    sizes: Tuple[int] = (2, 1),
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(
            text=i18n.back_button(),
            callback_data=MenuCallBack(level=level - 1, menu_name="catalog").pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=i18n.cart_button(),
            callback_data=MenuCallBack(level=3, menu_name="cart").pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=i18n.buy_button(),
            callback_data=MenuCallBack(
                level=level, menu_name="add_to_cart", product_id=product_id
            ).pack(),
        )
    )

    keyboard.adjust(*sizes)

    row = []

    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        category=category,
                        page=page + 1,
                    ).pack(),
                )
            )

        elif menu_name == "previous":
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        category=category,
                        page=page - 1,
                    ).pack(),
                )
            )

    return keyboard.row(*row).as_markup()


def get_callback_btns(*, btns: Dict[str, str], sizes: Tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_order_details_keyboard(orders, i18n):
    keyboard = []
    for order in orders:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=i18n.order_detail_button(order_id=str(order.id)[:8]),
                    callback_data=OrderDetailCallBack(order_id=str(order.id)).pack(),
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text=i18n.back_button(),
                callback_data=MenuCallBack(menu_name="main", level=1 - 1).pack(),
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_inline_back_button(i18n: TranslatorRunner):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.back_button(),
                    callback_data=MenuCallBack(menu_name="main", level=1 - 1).pack(),
                )
            ]
        ]
    )


def get_select_payment_keyboard(i18n: TranslatorRunner):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="TON 💎", callback_data="crypto_TON"),
                InlineKeyboardButton(text="BTC ₿", callback_data="crypto_BTC"),
            ],
            [
                InlineKeyboardButton(text="USDT 💵", callback_data="crypto_USDT"),
                InlineKeyboardButton(text="ETH ⟠", callback_data="crypto_ETH"),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.star_payment_btn(), callback_data="star_payment"
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.back_button(), callback_data="cancel_order"
                )
            ],
        ]
    )


def get_language_selection_keyboard(i18n: TranslatorRunner):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇺🇸 English",
                    callback_data=LanguageCallBack(language="en").pack(),
                ),
                InlineKeyboardButton(
                    text="🇷🇺 Русский",
                    callback_data=LanguageCallBack(language="ru").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.back_button(),
                    callback_data=MenuCallBack(menu_name="main", level=0).pack(),
                )
            ],
        ]
    )


def create_keyboard(*buttons, row_width=1):
    kb = []
    for i in range(0, len(buttons), row_width):
        row = buttons[i : i + row_width]
        kb.append(
            [InlineKeyboardButton(text=text, callback_data=data) for text, data in row]
        )
    return InlineKeyboardMarkup(inline_keyboard=kb)
