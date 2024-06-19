import asyncio
import os

from aiogram import Bot, Dispatcher
from typing import List
from aiogram import types
from aiogram.client.default import DefaultBotProperties

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from handlers.user_private import user_private_router
from common.bot_commands_list import private
from handlers.user_group import user_group_router
from aiogram.enums import ParseMode

ALLOWED_UPDATES: List[str] = ['message', 'edited_message']

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(user_group_router)


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot stopped')
