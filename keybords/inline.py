from typing import Dict, List, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.callbacks import MenuCallBack, OrderDetailCallBack


def get_user_main_btns(*, level: int, sizes: Tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Goods 🍕": "catalog",
        "Cart 🛒": "cart",
        "Orders 📦": "orders",
        "About us ℹ️": "about",
        "Payment 💰": "payment",
        "Delivery 🚚": "shipping",
        "Profile 👤": "profile",
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
                text="Delete",
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
                text="Main 🏠",
                callback_data=MenuCallBack(level=0, menu_name="main").pack(),
            ),
            InlineKeyboardButton(
                text="Order 🛍️",
                callback_data=MenuCallBack(level=0, menu_name="order").pack(),
            ),
        ]
        return keyboard.row(*row2).as_markup()
    else:
        keyboard.add(
            InlineKeyboardButton(
                text="Main 🏠",
                callback_data=MenuCallBack(level=0, menu_name="main").pack(),
            )
        )

        return keyboard.adjust(*sizes).as_markup()


def get_user_catalog_btns(
    *, level: int, categories: List[str], sizes: Tuple[int] = (2,)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(
            text="Back",
            callback_data=MenuCallBack(level=level - 1, menu_name="main").pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Cart 🛒", callback_data=MenuCallBack(level=3, menu_name="cart").pack()
        )
    )

    for c in categories:
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
    level: int,
    category: int,
    page: int,
    pagination_btns: dict,
    product_id: int,
    sizes: Tuple[int] = (2, 1),
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(
            text="Back",
            callback_data=MenuCallBack(level=level - 1, menu_name="catalog").pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Cart 🛒", callback_data=MenuCallBack(level=3, menu_name="cart").pack()
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Buy 💵",
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


def get_order_details_keyboard(orders):

    keyboard = []
    for order in orders:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"📋 Order details #{str(order.id)[:8]}",
                    callback_data=OrderDetailCallBack(order_id=str(order.id)).pack(),
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="◀️ Back",
                callback_data=MenuCallBack(menu_name="main", level=1-1).pack(),
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_inline_back_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data=MenuCallBack(menu_name="main", level=1-1).pack())]
        ]
    )


def get_select_payment_keyboard():
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
                InlineKeyboardButton(text="Star Payment ⭐", callback_data="star_payment")
            ],
            [InlineKeyboardButton(text="Back ⬅️", callback_data="cancel_order")]
        ]
    )
