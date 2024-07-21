import datetime
import random

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_to_cart, orm_add_user
from filters.chat_types import ChatTypeFilter
from handlers.admin_private import category_choice
from handlers.menu_processing import get_menu_content
from keybords.inline import MenuCallBack

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))

stickers = ["😒", "🤓", "😎", "😬", "😯", "😶"]

correct_sticker = {}
captcha_checked = {}


async def has_passed_captcha_recently(user_id: int, session: AsyncSession) -> bool:
    two_weeks_ago = datetime.datetime.now() - datetime.timedelta(minutes=1)
    query = text(
        """
            SELECT 1 FROM captcha 
            WHERE user_id = :user_id AND timestamp > :two_weeks_ago
        """
    )
    result = await session.execute(
        query, {"user_id": user_id, "two_weeks_ago": two_weeks_ago}
    )
    return result.scalar() is not None


async def ensure_user_exists(user_id: int, session: AsyncSession):
    user_exists_query = text(
        """
        SELECT EXISTS(SELECT 1 FROM "user" WHERE user_id = :user_id)
    """
    )
    user_exists_result = await session.execute(user_exists_query, {"user_id": user_id})
    user_exists = user_exists_result.scalar_one()

    if not user_exists:
        insert_user_query = text(
            """
            INSERT INTO "user" (user_id, first_name, last_name, phone) VALUES (:user_id, :first_name, :last_name, :phone)
        """
        )
        await session.execute(
            insert_user_query,
            {
                "user_id": user_id,
                "first_name": "Unknown",
                "last_name": "Unknown",
                "phone": "Unknown",
            },
        )
        await session.commit()


async def mark_captcha_passed(user_id: int, captcha_value: str, session: AsyncSession):
    await ensure_user_exists(user_id, session)

    current_time = datetime.datetime.now()
    query = text(
        """
        INSERT INTO captcha (user_id, captcha, timestamp)
        VALUES (:user_id, :captcha, :timestamp)
        ON CONFLICT (user_id)
        DO UPDATE SET captcha = EXCLUDED.captcha, timestamp = EXCLUDED.timestamp
    """
    )
    await session.execute(
        query, {"user_id": user_id, "captcha": captcha_value, "timestamp": current_time}
    )
    await session.commit()


@user_private_router.message(CommandStart())
async def captcha_cmd(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    if await has_passed_captcha_recently(user_id, session):
        await start_cmd(message, session)
    else:
        correct_sticker[user_id] = random.choice(stickers)
        captcha_checked[user_id] = False
        buttons = [
            InlineKeyboardButton(text=sticker, callback_data=sticker)
            for sticker in stickers
        ]
        rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
        await message.answer(
            f"<strong>Привет, подтверди, что Ты не робот,\n"
            f"выбери указанный смайл:</strong> {correct_sticker[user_id]} \n\n"
            f"<i>После прохождения капчи, получишь доступ к боту</i>",
            reply_markup=keyboard,
            parse_mode="HTML",
        )


async def check_captcha(callback: types.CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    if not captcha_checked.get(user_id, False):
        if callback.data == correct_sticker.get(user_id):
            await callback.answer("Captcha passed!")
            await callback.message.delete()
            await mark_captcha_passed(callback.from_user.id, callback.data, session)
            captcha_checked[user_id] = True
            await start_cmd(callback.message, session)
        else:
            await callback.answer("Wrong sticker. Try again.")


@user_private_router.callback_query()
async def process_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    user_id = callback.from_user.id
    if await has_passed_captcha_recently(user_id, session):
        try:
            callback_data = callback.data.split(":")
            if len(callback_data) == 1:
                await category_choice(callback, state, session)
            else:
                callback_data = MenuCallBack.unpack(callback.data)
                await user_menu(callback, callback_data, session)
        except ValueError:
            await callback.answer("Unrecognized action.", show_alert=True)
    else:
        await check_captcha(callback, session)


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession) -> None:
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")

    await message.answer_photo(
        media.media, caption=media.caption, reply_markup=reply_markup
    )


async def add_to_cart(
    callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession
):
    user = callback.from_user
    await orm_add_user(
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )

    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer("Product added to cart.")


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(
    callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession
):

    if callback_data.menu_name == "add_to_cart":
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
