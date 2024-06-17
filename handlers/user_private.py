from aiogram.filters import CommandStart, Command, or_f
from aiogram import types, Router, F
from filters.chat_types import ChatTypeFilter

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def on_startup(message: types.Message) -> None:
    await message.answer("Hello, I'm a virtual assistant. How can I help you?")


@user_private_router.message(Command('start'))
async def start(message: types.Message) -> None:
    await message.answer("Start:")


@user_private_router.message(F.text.lower() == 'menu')
@user_private_router.message(or_f(Command('menu'), (F.text.lower() == 'меню')))
async def menu(message: types.Message) -> None:
    await message.answer("Menu:")
    # await bot.send_message(message.from_user.id, message.text)
    # await message.reply(message.text)


@user_private_router.message(F.text.lower() == 'about us')
@user_private_router.message(Command('about'))
async def about(message: types.Message) -> None:
    await message.answer("About Us:")


@user_private_router.message(F.text.lower() == 'payment options')
@user_private_router.message(Command('payment'))
async def payment(message: types.Message) -> None:
    await message.answer("Payment Options:")


@user_private_router.message((F.text.lower().contains('delivery')) | (F.text.lower() == 'delivery options'))
@user_private_router.message(Command('shipping'))
async def shipping(message: types.Message) -> None:
    await message.answer("Delivery Options:")




