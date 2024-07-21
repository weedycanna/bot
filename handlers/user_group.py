from typing import Set

from aiogram import Bot, Router, types
from aiogram.filters import Command

from filters.chat_types import ChatTypeFilter
from utils.utils import clean_text, get_restricted_words

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))
user_group_router.edited_message.filter(ChatTypeFilter(["group", "supergroup"]))

restricted_words: Set[str] = get_restricted_words()


@user_group_router.message(Command("admin"))
async def get_admins(message: types.Message, bot: Bot) -> None:
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == "creator" or member.status == "administrator"
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()


@user_group_router.edited_message()
@user_group_router.message()
async def cleaner(message: types.Message) -> None:
    if restricted_words.intersection(clean_text(message.text.lower()).split()):
        await message.answer(
            f"{message.from_user.username}, keeps order in the chat! 🤬"
        )
        await message.delete()
        await message.chat.ban(message.from_user.id)
