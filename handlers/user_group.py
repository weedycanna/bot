from typing import Set
from filters.chat_types import ChatTypeFilter

from aiogram import types, Router

from utils import get_restricted_words, clean_text

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))

restricted_words: Set[str] = get_restricted_words()


@user_group_router.edited_message()
@user_group_router.message()
async def cleaner(message: types.Message) -> None:
    if restricted_words.intersection(clean_text(message.text.lower()).split()):
        await message.answer(f'{message.from_user.username}, keeps order in the chat! 🤬')
        await message.delete()
        await message.chat.ban(message.from_user.id)

