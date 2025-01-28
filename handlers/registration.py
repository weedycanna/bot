import random

import phonenumbers
from aiogram.filters import CommandStart, StateFilter
from phonenumbers import NumberParseException

from handlers.captcha import captcha_checked, correct_sticker, stickers
from handlers.start_cmd import start_cmd
from queries.captcha_queries import has_passed_captcha_recently
from queries.user_queries import create_telegram_user
from states.registration_state import RegistrationStates
import os
from typing import Union
from django.utils import timezone

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    ReplyKeyboardRemove,
)
from django.conf import settings
from django_project.telegrambot.usersmanage.models import Order, CaptchaRecord
from filters.chat_types import ChatTypeFilter
from keybords.inline import MenuCallBack, get_inline_back_button
from keybords.reply import get_back_button
from queries.banner_queries import get_banner
from queries.user_queries import get_user




registration_router = Router()
registration_router.message.filter(ChatTypeFilter(["private"]))


@registration_router.message(CommandStart())
async def start_registration(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    user = await get_user(user_id)

    if user:
        if await has_passed_captcha_recently(user_id):
            await start_cmd(message)
            return
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
                f"<strong>Hello, please confirm that you are not a robot,\n"
                f"choose the indicated emoji:</strong> {correct_sticker[user_id]} \n\n"
                f"<i>After passing the captcha, you will get access to the bot</i>",
                reply_markup=keyboard,
                parse_mode="HTML",
            )
            return

    await state.set_state(RegistrationStates.first_name)
    await message.answer(
        "🙌 Hello, glad to see you 🙌\n\n"
        "This bot will help you access the menu of our pizzeria 🍕\n"
        "You can also place an order and get information about us 📋\n\n\n"
        "All this and more will be available after registration 🔽✅\n"
        "Please enter your name:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )


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
        phone_number = phonenumbers.parse(message.text, None)
        if not phonenumbers.is_valid_number(phone_number):
            raise ValueError("Invalid phone number format")

        user_data = await state.get_data()
        formatted_phone = phonenumbers.format_number(
            phone_number, phonenumbers.PhoneNumberFormat.E164
        )

        user_id = message.from_user.id
        user = await create_telegram_user(
            phone_number=formatted_phone,
            first_name=user_data["first_name"],
            user_id=user_id,
        )

        if not user:
            await message.answer(
                "❌ A user with this phone number or Telegram ID already exists. "
                "Please check your data or contact the administrator."
            )
            return

        await state.clear()

        correct_sticker[user_id] = random.choice(stickers)
        captcha_checked[user_id] = False

        buttons = [
            InlineKeyboardButton(text=sticker, callback_data=sticker)
            for sticker in stickers
        ]
        rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

        await message.answer(
            f"<strong>✅ Registration successful!</strong>\n\n"
            f"<strong>Confirm that you are not a robot.\n"
            f"Choose the indicated emoji:</strong> {correct_sticker[user_id]}\n"
            f"<i>After passing the captcha you will get access to the bot</i>",
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    except NumberParseException:
        await message.answer(
            "❌ Invalid phone number format. Please enter the number in international format "
            "(for example, +79123456789):"
        )
    except ValueError:
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
            f"⚙️ Firstname: <code>{update.from_user.first_name}</code>\n"
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
