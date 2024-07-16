import random

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart, or_f
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.formatting import Bold, as_list, as_marked_section
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_to_cart, orm_add_user, orm_get_products
from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from keybords.inline import MenuCallBack, get_callback_btns
from keybords.reply import get_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))

stickers = ['😒', '🤓', '😎', '😬', '😯', '😶']

correct_sticker = None
captcha_checked = False


@user_private_router.message(CommandStart())
async def captcha_cmd(message: types.Message, session: AsyncSession):
    global correct_sticker, captcha_checked
    correct_sticker = random.choice(stickers)
    captcha_checked = False

    buttons = [InlineKeyboardButton(text=sticker, callback_data=sticker) for sticker in stickers]
    rows = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    await message.answer(f'<strong>Привет, подтверди, что Ты не робот,\n'
                         f'выбери указанный смайл:</strong> {correct_sticker} \n\n'
                         f'<i>После прохождения капчи, получишь доступ к боту</i>',
                         reply_markup=keyboard, parse_mode='HTML')


async def check_captcha(callback: types.CallbackQuery, session: AsyncSession):
    global correct_sticker, captcha_checked
    if not captcha_checked:
        if callback.data == correct_sticker:
            await callback.answer("Captcha passed!")
            await callback.message.delete()
            await start_cmd(callback.message, session)
            captcha_checked = True
        else:
            await callback.answer("Wrong sticker. Try again.")


@user_private_router.callback_query()
async def process_callback(callback: types.CallbackQuery, session: AsyncSession):
    if not captcha_checked:
        await check_captcha(callback, session)
    else:
        callback_data = MenuCallBack.unpack(callback.data)
        await user_menu(callback, callback_data, session)


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession) -> None:
    media, reply_markup = await get_menu_content(session, level=0, menu_name='main')

    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)

    # await message.answer("Hello, I'm a virtual assistant. How can I help you?",
    #                      reply_markup=get_callback_btns(btns={
    #                          'Click me: ': 'some_1'
    #                      }))


async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user
    await orm_add_user(
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )

    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer('Product added to cart.')


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):

    if callback_data.menu_name == 'add_to_cart':
        await add_to_cart(callback, callback_data, session)
        return

    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()




# @user_private_router.callback_query(F.data.startswith('some_'))
# async def counter(callback: types.CallbackQuery):
#     number = int(callback.data.split('_')[-1])
#
#     await callback.message.edit_text(
#         text=f"Counter - {number}",
#         reply_markup=get_callback_btns(btns={
#             'Click one more: ': f'some_{number + 1}'
#         }))


# @user_private_router.message(CommandStart())
# async def on_startup(message: types.Message) -> None:
#     await message.answer("Hello, I'm a virtual assistant. How can I help you?",
#                          reply_markup=get_keyboard(
#                                 "📖 Menu",
#                                 "ℹ️ About",
#                                 "💰 Payment Options",
#                                 "📦 Delivery Options",
#                                 "👤 Personal Info",
#                                 placeholder="What are you interested in?",
#                                 request_contact=4,
#                                 request_location=5,
#                                 sizes=(2, 2)
#                             ))
#
#
# @user_private_router.message((F.text.lower().contains('menu') | (F.text.lower() == 'menu')))
# @user_private_router.message(or_f(Command('menu'), (F.text.lower() == 'меню')))
# async def menu(message: types.Message, session: AsyncSession) -> None:
#     for product in await orm_get_products(session):
#         await message.answer_photo(
#             product.image,
#             caption=f"<strong>{product.name}\
#                        </strong>\n{product.description}\nPrice: {round(product.price, 2)}$",
#         )
#     await message.answer("Menu:")
#     # await bot.send_message(message.from_user.id, message.text)
#     # await message.reply(message.text)
#
#
# @user_private_router.message((F.text.lower().contains('about')) | (F.text.lower() == 'about'))
# @user_private_router.message(Command('about'))
# async def about(message: types.Message) -> None:
#     await message.answer("About Us:")


# @user_private_router.message((F.text.lower().contains('payment options')) | (F.text.lower() == 'delivery options'))
# @user_private_router.message(Command('payment'))
# async def payment(message: types.Message) -> None:
#     text = as_marked_section(
#         Bold('Payment Options:'),
#         'Card in Bot',
#         'Cash/Cart Payment',
#         'Cryptocurrency Payment',
#         marker='✅ '
#     )
#     await message.answer(text.as_html())
#
#
# @user_private_router.message((F.text.lower().contains('delivery')) | (F.text.lower() == 'delivery options'))
# @user_private_router.message(Command('shipping'))
# async def shipping(message: types.Message) -> None:
#     text = as_list(
#         as_marked_section(
#             Bold('Delivery Options:'),
#             'Pickup',
#             'Courier',
#             'Post',
#             marker='✅ '
#         ),
#         as_marked_section(
#             Bold('Cancel:'),
#             'Pigeons',
#             'Teleport',
#             marker='❌ '
#         ),
#         sep='\n----------------\n'
#     )
#     await message.answer(text.as_html())
#
#
# @user_private_router.message((F.text.lower().contains('personal info')) | (F.text.lower() == 'personal info'))
# @user_private_router.message(Command('personal_info'))
# async def personal_info(message: types.Message) -> None:
#     await message.answer("Personal Info:", reply_markup=get_keyboard(
#         "📱 Send Phone Number",
#         "🗺 Send Location",
#         placeholder="What do you want to send?",
#         request_contact=0,
#         request_location=1,
#         sizes=(2, 2)
#     ))
#
#
# @user_private_router.message(F.contact)
# async def contact(message: types.Message) -> None:
#     await message.answer(f'Number got: {str(message.contact)}')
#
#
# @user_private_router.message(F.location)
# async def location(message: types.Message) -> None:
#     await message.answer(f'Location got: {str(message.location)}')
