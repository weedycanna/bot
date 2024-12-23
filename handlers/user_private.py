import asyncio
import datetime
import random

from aiogram import Router, types, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, Union

from queries.banner_queries import orm_get_banner
from queries.cart_queries import orm_add_to_cart
from filters.chat_types import ChatTypeFilter
from handlers.admin_private import category_choice
from handlers.menu_processing import get_menu_content
from keybords.inline import MenuCallBack, get_user_catalog_btns
from queries.category_queries import orm_get_categories
from queries.user_queries import orm_add_user

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))

stickers = ["😒", "🤓", "😎", "😬", "😯", "😶"]

correct_sticker = {}
captcha_checked = {}


async def has_passed_captcha_recently(user_id: int, session: AsyncSession) -> bool:
    two_weeks_ago = datetime.datetime.now() - datetime.timedelta(days=14)
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


@user_private_router.message(Command(commands=["menu", "cart", "about", "payment", "shipping"]))
@user_private_router.callback_query(MenuCallBack.filter())
async def process_menu_command(update: Union[CallbackQuery, Message], session: AsyncSession):
    try:

        if isinstance(update, CallbackQuery):
            callback_data = MenuCallBack.unpack(update.data)
            menu_name = callback_data.menu_name
            level = callback_data.level
            category = callback_data.category
            page = callback_data.page
            product_id = callback_data.product_id
            user_id = update.from_user.id
            target = update.message
            is_callback = True
        else:
            menu_name = update.text[1:]
            level = 0 if menu_name != "menu" else 1
            category = None
            page = None
            product_id = None
            user_id = update.from_user.id
            target = update
            is_callback = False

        if not is_callback and menu_name == "menu":
            try:
                categories = await orm_get_categories(session)
                if not categories:
                    await target.answer("Категории не найдены")
                    return

                banner = await orm_get_banner(session, menu_name)

                if banner and banner.image:
                    await target.answer_photo(
                        photo=banner.image,
                        caption=f"<b>{banner.description}</b>\n\nВыберите категорию:",
                        reply_markup=get_user_catalog_btns(level=1, categories=categories),
                        parse_mode="HTML"
                    )
                else:
                    await target.answer(
                        text="Выберите категорию:",
                        reply_markup=get_user_catalog_btns(level=1, categories=categories),
                        parse_mode="HTML"
                    )
                return
            except Exception as e:
                await target.answer("Произошла ошибка при загрузке меню")
                return

        image, keyboard = await get_menu_content(
            session=session,
            level=level,
            menu_name=menu_name,
            category=category,
            page=page,
            product_id=product_id,
            user_id=user_id
        )

        if is_callback:
            await target.edit_media(
                media=image,
                reply_markup=keyboard
            )
            await update.answer()
        else:
            await target.answer_photo(
                photo=image.media,
                caption=image.caption,
                reply_markup=keyboard,
                parse_mode="HTML"
            )

    except Exception as e:
        error_message = f"Произошла ошибка при открытии меню {menu_name}"
        if is_callback:
            await update.answer(error_message, show_alert=True)
        else:
            await target.answer(error_message)


@user_private_router.message(Command("clear"))
async def clear_private_user(message: types.Message, bot: Bot) -> None:
    try:
        if message.chat.type != "private":
            return

        command, *args = message.text.split()
        num_messages = int(args[0]) if args and args[0].isdigit() else 10

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
