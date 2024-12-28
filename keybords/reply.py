from typing import Tuple

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard(
    *btns: str,
    placeholder: str = None,
    request_contact: int = None,
    request_location: int = None,
    sizes: Tuple[int] = (2,),
):

    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )


def get_back_button():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Back")]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
