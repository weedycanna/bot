import asyncio
import logging
import os
from typing import List

import betterlogging as bt
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from aiogram.enums import ParseMode

# from common.bot_commands_list import private
from database.engine import create_db, drop_db, session_maker
from middlewares.dp import DataBaseSession

# ALLOWED_UPDATES: List[str] = ['message', 'edited_message', 'callback_query']

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = []

dp = Dispatcher()

# dp.update.outer_middleware(CounterMiddleware())

# admin_router.message.outer_middleware(CounterMiddleware())


async def on_startup(bot):

    from handlers.admin_private import admin_router
    from handlers.user_group import user_group_router
    from handlers.user_private import user_private_router

    dp.include_router(user_private_router)
    dp.include_router(user_group_router)
    dp.include_router(admin_router)

    run_param = False
    if run_param:
        await drop_db()

    # await drop_db()
    await create_db()


async def on_shutdown(bot):
    print('Bot stopped')


async def main() -> None:
    bt.basic_colorized_config(level=logging.INFO)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    # await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ...
