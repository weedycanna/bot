import os
from typing import Union

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, FSInputFile, InputMediaPhoto,
                           Message, ReplyKeyboardRemove)
from django.conf import settings
from django.utils import timezone
from phonenumbers import NumberParseException

from app import CHANNEL_LINK
from django_project.telegrambot.usersmanage.models import CaptchaRecord, Order
from filters.chat_types import ChatTypeFilter
from handlers.captcha import (has_passed_captcha_recently, send_captcha,
                              stickers, word_to_sticker, words)
from handlers.check_subscription import check_subscription
from handlers.start_cmd import start_cmd
from keybords.inline import MenuCallBack, get_inline_back_button
from keybords.reply import create_keyboard, get_back_button
from queries.banner_queries import get_banner
from queries.user_queries import create_telegram_user, get_user
from states.registration_state import RegistrationStates
from utils.utils import format_phone_number

registration_router = Router()
registration_router.message.filter(ChatTypeFilter(["private"]))


@registration_router.message(CommandStart())
async def start_registration(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if user and user.phone_number:
        if await has_passed_captcha_recently(user_id):
            await start_cmd(message)
        else:
            await send_captcha(message, user_id, words, word_to_sticker, stickers)
        return

    if not await has_passed_captcha_recently(user_id):
        await send_captcha(message, user_id, words, word_to_sticker, stickers)
        return

    await message.answer("Please enter your name:")
    await state.set_state(RegistrationStates.first_name)


@registration_router.message(StateFilter(RegistrationStates.first_name))
async def process_first_name(message: types.Message, state: FSMContext):
    if len(message.text) > 30:
        await message.answer(
            "❌ The name is too long. Please enter a name shorter than 30 characters."
        )
        return

    await state.update_data(first_name=message.text)
    await state.set_state(RegistrationStates.phone)
    await message.answer(
        "Now, please enter your phone number\n"
        "📱 The phone number format should be +7xxxxxxxxxx \n"
        "⚠️ Attention! The phone number must be unique",
        reply_markup=get_back_button(),
        parse_mode="HTML",
    )


@registration_router.message(StateFilter(RegistrationStates.phone))
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Back":
        await state.set_state(RegistrationStates.first_name)
        await message.answer(
            "Please enter your name:", reply_markup=ReplyKeyboardRemove()
        )
        return

    try:
        formatted_phone = format_phone_number(message.text)
        if not formatted_phone:
            await message.answer(
                "❌ Invalid phone number format. Please enter the number in international format\n"
                "Examples:\n"
                "+380 XX XXX XXXX\n"
                "+7 XXX XXX XXXX"
            )
            return

        user_data = await state.get_data()

        user_id = message.from_user.id
        user = await create_telegram_user(
            user_id=user_id,
            first_name=user_data["first_name"],
            phone_number=formatted_phone
        )

        if not user:
            await message.answer(
                "❌ This phone number is already registered with another account. "
                "Please use a different phone number or contact the administrator."
            )
            return

        await state.clear()

        await message.answer(
            "✅ Registration completed successfully!\n"
            f"Name: {user_data['first_name']}\n"
            f"Phone: {formatted_phone}"
        )

        if await check_subscription(user_id):
            await start_cmd(message)
        else:
            kb = create_keyboard(("🔄 Check subscription", "check_subscription"))
            await message.answer(
                f"🚫 Please subscribe to the channels to use the bot:\n[Subscribe to the channel]({CHANNEL_LINK})",
                reply_markup=kb,
                parse_mode='Markdown'
            )

    except NumberParseException:
        await message.answer(
            "❌ Invalid phone number format. Please enter the number in international format "
            "(for example, +79123456789):"
        )
    except ValueError:
        await message.answer(
            "❌ Invalid phone number format. Please try again."
        )
    except Exception:
        await message.answer(
            "❌ An error occurred during registration. Please try again later."
        )


@registration_router.message(Command("profile"))
@registration_router.callback_query(MenuCallBack.filter(F.menu_name == "profile"))
async def process_profile_command(update: Union[CallbackQuery, Message]):
    try:
        if isinstance(update, CallbackQuery):
            user_id = update.from_user.id
            target = update.message
            is_callback = True
        else:
            user_id = update.from_user.id
            target = update
            is_callback = False

        user = await get_user(user_id)
        orders = Order.objects.filter(user_id=user.id)

        captcha_status = CaptchaRecord.objects.filter(user_id=user.id).first()
        captcha_status_text = "✅ Passed" if (captcha_status and captcha_status.is_passed) else "❌ Not passed"

        days_in_bot = (timezone.now() - user.created_at).days

        profile_text = (
            f"<b>⚡️ Profile</b>\n"
            f"👉🏼 ID: <code>{user_id}</code>\n"
            f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            f"⚙️ Fullname: <code>{update.from_user.first_name} {update.from_user.last_name}</code>\n"
            f"🎮 Username: <code>@{update.from_user.username}</code>\n"
            f"📱 Phone: <code>{user.phone_number}</code>\n"
            f"🔐 Captcha: <code>{captcha_status_text}</code>\n"
            f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            f"📊 Statistics:\n"
            f"📅 Days in bot: <code>{days_in_bot}</code>\n"
            f"📦 Total orders: <code>{len(orders)}</code>\n"
            f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            f"📆 Registration date: <code>{user.created_at.strftime('%d.%m.%Y')}</code>"
        )

        banner = await get_banner("profile")

        if not banner:
            raise ValueError("Banner not found")

        if not banner.image:
            raise ValueError("Banner has no image")

        image_path = os.path.join(settings.MEDIA_ROOT, str(banner.image))
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Banner image not found: {image_path}")

        media = InputMediaPhoto(
            media=FSInputFile(image_path),
            caption=profile_text,
            parse_mode="HTML",
        )

        if is_callback:
            keyboard = get_inline_back_button()
            await target.edit_media(media=media, reply_markup=keyboard)
            await update.answer()
        else:
            keyboard = get_back_button()
            await target.answer_photo(
                photo=FSInputFile(image_path),
                caption=profile_text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )

    except (FileNotFoundError, AttributeError, OSError, TypeError):
        await update.answer(
            "An error occurred while loading the profile", show_alert=True
        )
