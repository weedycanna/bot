import asyncio
import logging
import os

import betterlogging as bt
import django
from aiocryptopay import AioCryptoPay, Networks
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()


bot = Bot(
    token=os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


CRYPTO_TOKEN = os.getenv("CRYPTO_TOKEN")
crypto_client = AioCryptoPay(CRYPTO_TOKEN, network=Networks.TEST_NET)

bot.my_admins_list: list[int, ] = []
CHANNEL_ID: str = os.getenv("CHANNEL_ID")
CHANNEL_LINK: str = os.getenv("CHANNEL_LINK")


dp = Dispatcher()


async def on_startup(bot):
    from django.core.management import call_command

    from handlers.admin_private import admin_router
    from handlers.captcha import captcha_router
    from handlers.check_subscription import subscription_router
    from handlers.orders import order_router
    from handlers.registration import registration_router
    from handlers.user_group import user_group_router
    from handlers.user_private import user_private_router

    dp.include_router(admin_router)
    dp.include_router(registration_router)
    dp.include_router(captcha_router)
    dp.include_router(subscription_router)
    dp.include_router(order_router)
    dp.include_router(user_private_router)
    dp.include_router(user_group_router)

    call_command("migrate")

    call_command("loaddata", "fixtures/categories.json")
    call_command("loaddata", "fixtures/products.json")
    call_command("loaddata", "fixtures/banners.json")


async def on_shutdown(bot):
    print("\033[31mBot stopped!")


def setup_django():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "django_project.telegrambot.telegrambot.settings"
    )
    os.environ.update({"DJANGO_ALLOW_ASYNC_UNSAFE": "true"})

    django.setup()


async def main() -> None:
    bt.basic_colorized_config(level=logging.INFO)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        setup_django()
        asyncio.run(main())
    except KeyboardInterrupt:
        ...
