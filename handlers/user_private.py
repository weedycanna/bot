from aiogram.filters import CommandStart, Command, or_f
from aiogram import types, Router, F
from filters.chat_types import ChatTypeFilter
from keybords.reply import start_kb, del_kbd, start_kb2, start_kb3, data_kb
from aiogram.utils.formatting import as_marked_list, Bold, as_marked_section, as_list

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def on_startup(message: types.Message) -> None:
    await message.answer("Hello, I'm a virtual assistant. How can I help you?",
                         reply_markup=start_kb3.as_markup(
                             resize_keyboard=True,
                             input_field_placeholder='What are you interested in ?'
                         ))


@user_private_router.message((F.text.lower().contains('menu') | (F.text.lower() == 'menu')))
@user_private_router.message(or_f(Command('menu'), (F.text.lower() == 'меню')))
async def menu(message: types.Message) -> None:
    await message.answer("Menu:", reply_markup=del_kbd)
    # await bot.send_message(message.from_user.id, message.text)
    # await message.reply(message.text)


@user_private_router.message((F.text.lower().contains('about')) | (F.text.lower() == 'about'))
@user_private_router.message(Command('about'))
async def about(message: types.Message) -> None:
    await message.answer("About Us:")


@user_private_router.message((F.text.lower().contains('payment options')) | (F.text.lower() == 'delivery options'))
@user_private_router.message(Command('payment'))
async def payment(message: types.Message) -> None:
    text = as_marked_section(
        Bold('Payment Options:'),
        'Card in Bot',
        'Cash/Cart Payment',
        'Cryptocurrency Payment',
        marker='✅ '
    )
    await message.answer(text.as_html())


@user_private_router.message((F.text.lower().contains('delivery')) | (F.text.lower() == 'delivery options'))
@user_private_router.message(Command('shipping'))
async def shipping(message: types.Message) -> None:
    text = as_list(
        as_marked_section(
            Bold('Delivery Options:'),
            'Pickup',
            'Courier',
            'Post',
            marker='✅ '
        ),
        as_marked_section(
            Bold('Cancel:'),
            'Pigeons',
            'Teleport',
            marker='❌ '
        ),
        sep='\n----------------\n'
    )
    await message.answer(text.as_html())


@user_private_router.message((F.text.lower().contains('personal info')) | (F.text.lower() == 'personal info'))
@user_private_router.message(Command('personal_info'))
async def personal_info(message: types.Message) -> None:
    await message.answer("Personal Info:", reply_markup=data_kb)


@user_private_router.message(F.contact)
async def contact(message: types.Message) -> None:
    await message.answer(f'Number got: {str(message.contact)}')


@user_private_router.message(F.location)
async def location(message: types.Message) -> None:
    await message.answer(f'Location got: {str(message.location)}')
