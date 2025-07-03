from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from fluentogram import TranslatorRunner


def get_admin_keyboard(i18n: TranslatorRunner) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    button_keys = [
        "admin_add_good",
        "admin_assortment",
        "admin_add_banner",
        "admin_statistics",
        "admin_newsletter",
    ]

    for key in button_keys:
        builder.button(text=i18n.get(key))

    builder.adjust(2)

    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder=i18n.admin_kb_placeholder()
    )


def get_back_button(i18n: TranslatorRunner):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=i18n.back_button())]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
