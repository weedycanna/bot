from typing import Dict, Tuple

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.filters.callback_data import CallbackData


class MenuCallBack(CallbackData, prefix='menu'):
    level: int
    menu_name: str


def get_user_main_btns(*, level: int, sizes: Tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        'Goods 🛍': 'catalog',
        'Cart 🛒': 'cart',
        'About us 📖': 'about',
        'Payment 💰': 'payment',
        'Delivery 🚚': 'shipping',
    }
    for text, menu_name in btns.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=level + 1, menu_name=menu_name).pack()))
        elif menu_name == 'cart':
            keyboard.add(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=3, menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=level, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_callback_btns(
    *,
    btns: Dict[str, str],
    sizes: Tuple[int] = (2,),):

    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():

        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


# def get_url_btns(
#     *,
#     btns: Dict[str, str],
#     sizes: Tuple[int] = (2,),):
#
#     keyboard = InlineKeyboardBuilder()
#
#     for text, url in btns.values():
#
#         keyboard.add(InlineKeyboardButton(text=text, url=url))
#
#     return keyboard.adjust(*sizes).as_markup()


# Create mix from Callback and URL buttons

# def get_inline_mix_btns(
#     *,
#     btns: Dict[str, str],
#     sizes: Tuple[int] = (2,)):
#
#     keyboard = InlineKeyboardBuilder()
#
#     for text, value in btns.items():
#         if '://' in value:
#             keyboard.add(InlineKeyboardButton(text=text, url=value))
#         else:
#             keyboard.add(InlineKeyboardButton(text=text, callback_data=value))
#
#     return keyboard.adjust(*sizes).as_markup()
