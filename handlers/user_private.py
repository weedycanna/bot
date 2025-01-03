import asyncio
from typing import Union

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from django_project.telegrambot.usersmanage.models import Banner
from filters.chat_types import ChatTypeFilter
from handlers.admin_private import category_choice
from handlers.captcha import check_captcha
from handlers.menu_processing import get_menu_content
from keybords.inline import MenuCallBack, get_user_catalog_btns
from queries.banner_queries import get_banner
from queries.captcha_queries import has_passed_captcha_recently
from queries.cart_queries import add_to_cart
from queries.category_queries import get_categories
from queries.user_queries import add_user, get_user

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.callback_query()
async def process_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await has_passed_captcha_recently(user_id):
        try:
            callback_data = callback.data.split(":")
            if len(callback_data) == 1:
                await category_choice(callback, state)
            else:
                callback_data = MenuCallBack.unpack(callback.data)
                await user_menu(callback, callback_data)
        except ValueError:
            await callback.answer("Unrecognized action.", show_alert=True)
    else:
        await check_captcha(callback)


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message) -> None:
    media, reply_markup = await get_menu_content(level=0, menu_name="main")

    await message.answer_photo(
        media.media, caption=media.caption, reply_markup=reply_markup
    )


async def get_add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack):
    user = callback.from_user

    db_user = await get_user(user.id)

    if db_user is None:
        db_user = await add_user(
            user_id=user.id,
            first_name=user.first_name,
            phone=None,
        )

    if db_user is None:
        await callback.answer("Error adding user to the database.")
        return

    db_user = await get_user(user.id)
    if db_user is None:
        await callback.answer("User not found in the database after adding.")
        return

    cart_item = await add_to_cart(user.id, callback_data.product_id)

    if cart_item:
        await callback.answer("Product added to cart.")
    else:
        await callback.answer("Error adding product to cart.")


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack):
    if callback_data.menu_name == "add_to_cart":
        await get_add_to_cart(callback, callback_data)
        return

    media, reply_markup = await get_menu_content(
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


@user_private_router.message(
    Command(commands=["menu", "cart", "about", "payment", "shipping"])
)
@user_private_router.callback_query(MenuCallBack.filter())
async def process_menu_command(update: Union[CallbackQuery, Message]):
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
                categories = await get_categories()
                if not categories:
                    await target.answer("Categories not found")
                    return

                banner = await get_banner(menu_name)

                if banner and banner.image:
                    await target.answer_photo(
                        photo=banner.image,
                        caption=f"<b>{banner.description}</b>\n\nSelect a category:",
                        reply_markup=get_user_catalog_btns(
                            level=1, categories=categories
                        ),
                        parse_mode="HTML",
                    )
                else:
                    await target.answer(
                        text="Select a category:",
                        reply_markup=get_user_catalog_btns(
                            level=1, categories=categories
                        ),
                        parse_mode="HTML",
                    )
                return
            except Banner.DoesNotExist:
                await target.answer("Error loading menu")
                return

        image, keyboard = await get_menu_content(
            level=level,
            menu_name=menu_name,
            category=category,
            page=page,
            product_id=product_id,
            user_id=user_id,
        )

        if is_callback:
            await target.edit_media(media=image, reply_markup=keyboard)
            await update.answer()
        else:
            await target.answer_photo(
                photo=image.media,
                caption=image.caption,
                reply_markup=keyboard,
                parse_mode="HTML",
            )

    except (FileNotFoundError, AttributeError, OSError, TypeError):
        error_message = f"Error opening menu {menu_name}"
        await update.answer(error_message, show_alert=True)


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
            notification = await message.answer(f"Deleted {deleted_count} messages!")
            await asyncio.sleep(3)
            try:
                await notification.delete()
            except TelegramBadRequest:
                pass

    except ValueError:
        await message.answer("Invalid command format. Use: /clear or /clear <number>")
