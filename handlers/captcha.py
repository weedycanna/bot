from typing import Any

from aiogram.filters import CommandStart

from asgiref.sync import sync_to_async
from django.utils import timezone

from app import CHANNEL_LINK
from django_project.telegrambot.usersmanage.models import CaptchaRecord
from filters.chat_types import ChatTypeFilter
from handlers.check_subscription import check_subscription
from handlers.start_cmd import start_cmd
from keybords.reply import create_keyboard
from queries.captcha_queries import mark_captcha_passed
from queries.user_queries import add_user, get_user
from states.registration_state import RegistrationStates
from aiogram.types import Message

import random

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove



captcha_router = Router()
captcha_router.message.filter(ChatTypeFilter(["private"]))


stickers: list[Any] = ["🍎", "🚗", "🍬", "⚽", "🪑", "⌚"]
words: list[Any] = ["apple", "car", "candy", "ball", "chair", "watch"]
correct_sticker: dict = {}
captcha_checked: dict = {}

word_to_sticker = dict(zip(words, stickers))


async def has_passed_captcha_recently(user_id: int) -> bool:
    try:
        two_weeks_ago = timezone.now() - timezone.timedelta(weeks=2)
        user = await get_user(user_id)
        if not user:
            return False

        record = await sync_to_async(
            CaptchaRecord.objects.filter(
                user=user, timestamp__gt=two_weeks_ago, is_passed=True
            ).exists
        )()

        return record
    except CaptchaRecord.DoesNotExist:
        return False


async def send_captcha(message: Message, user_id: int, words: list, word_to_sticker: dict, stickers: list) -> None:
    correct_word = random.choice(words)
    correct_sticker[user_id] = word_to_sticker[correct_word]
    captcha_checked[user_id] = False

    buttons = [
        InlineKeyboardButton(text=sticker, callback_data=sticker)
        for sticker in stickers
    ]
    rows = [buttons[i: i + 3] for i in range(0, len(buttons), 3)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    await message.answer(
        f"Hello! Before we begin,\n"
        f"please confirm that you are not a robot.\n"
        f"Select the specified word:<strong> {correct_word}</strong>\n\n"
        f"<i>After passing the captcha, you can proceed with registration</i>",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def check_captcha(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    try:
        if callback.data == correct_sticker.get(user_id):
            if await mark_captcha_passed(user_id, callback.data):
                await callback.answer("Captcha passed successfully!")
                await callback.message.delete()
                captcha_checked[user_id] = True

                user = await get_user(user_id)
                if user and user.phone_number:
                    if await check_subscription(user_id):
                        await start_cmd(callback.message)
                    else:
                        kb = create_keyboard(("🔄 Check subscription", "check_subscription"))
                        await callback.message.answer(
                            f"🚫 Please subscribe to the channels to use the bot:\n[Subscribe to the channel]({CHANNEL_LINK})",
                            reply_markup=kb,
                            parse_mode='Markdown'
                        )
                else:
                    await state.set_state(RegistrationStates.first_name)
                    await callback.message.answer(
                        "🙌 Hello, glad to see you 🙌\n\n"
                        "This bot will help you access the menu of our pizzeria 🍕\n"
                        "You can also place an order and get information about us 📋\n\n\n"
                        "All this and more will be available after registration 🔽✅\n"
                        "Please enter your name:",
                        reply_markup=ReplyKeyboardRemove(),
                        parse_mode="HTML",
                    )
            else:
                await callback.answer("Error saving captcha status. Please try again.")
        else:
            await callback.answer("Wrong selection. Please try again.")
    except Exception:
        await callback.answer("An error occurred. Please try again.")



@captcha_router.message(CommandStart())
async def captcha_cmd(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Unknown"
    user = await get_user(user_id)

    if not user:
        user = await add_user(
            user_id=user_id,
            first_name=first_name,
        )

    if user is None:
        await message.answer("Error creating user. Please try again.")
        return

    if await has_passed_captcha_recently(user_id):
        if await check_subscription(user_id):
            await start_cmd(message)
        else:
            kb = create_keyboard(("🔄 Check subscription", "check_subscription"))
            await message.answer(
                f"🚫 Please subscribe to the channels to use the bot:\n[Subscribe to the channel]({CHANNEL_LINK})",
                reply_markup=kb,
                parse_mode='Markdown'
            )
    else:
        await send_captcha(message, user_id, words, word_to_sticker, stickers)

