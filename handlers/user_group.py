import asyncio
from typing import Set

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
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


@user_group_router.message(Command("clear"))
async def clear_group(message: types.Message, bot: Bot) -> None:
    try:
        command, *args = message.text.split()
        num_messages = int(args[0]) if args and args[0].isdigit() else 10

        is_private = message.chat.type == "private"

        if not is_private:
            chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
            if chat_member.status not in ['administrator', 'creator']:
                await message.answer("Команда доступна только администраторам группы")
                return

            bot_member = await bot.get_chat_member(message.chat.id, (await bot.me()).id)
            if bot_member.status not in ['administrator', 'creator']:
                await message.answer("Бот должен быть администратором группы для удаления сообщений")
                return

        deleted_count = 0
        for i in range(num_messages):
            try:
                message_id = message.message_id - i
                await bot.delete_message(message.chat.id, message_id)
                deleted_count += 1
            except TelegramBadRequest:
                continue

        if deleted_count > 0:
            notification = await message.answer(f"Удалено {deleted_count} сообщений!")
            await asyncio.sleep(3)
            try:
                await notification.delete()
            except TelegramBadRequest:
                pass

    except ValueError:
        await message.answer("Неверный формат команды. Используйте: /clear или /clear <число>")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")



@user_group_router.edited_message()
@user_group_router.message()
async def cleaner(message: types.Message) -> None:
    if restricted_words.intersection(clean_text(message.text.lower()).split()):
        first_name = message.from_user.first_name or ""
        last_name = message.from_user.last_name or ""
        full_name = f"{first_name} {last_name}"

        await message.answer(
            f"{full_name}, keeps order in the chat! 🤬"
        )

        await message.delete()
        await message.chat.ban(message.from_user.id)


