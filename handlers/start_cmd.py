from aiogram import types
from fluentogram import TranslatorRunner

from handlers.menu_processing import get_menu_content


async def start_cmd(message: types.Message, i18n: TranslatorRunner) -> None:
    media, reply_markup = await get_menu_content(
        level=0,
        menu_name="main",
        i18n=i18n,
    )
    await message.answer_photo(
        media.media, caption=media.caption, reply_markup=reply_markup
    )
