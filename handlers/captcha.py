import random

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from django_project.telegrambot.usersmanage.models import CaptchaRecord
from filters.chat_types import ChatTypeFilter
from handlers.start_cmd import start_cmd
from queries.captcha_queries import has_passed_captcha_recently, mark_captcha_passed
from queries.user_queries import add_user, get_user

captcha_router = Router()
captcha_router.message.filter(ChatTypeFilter(["private"]))


stickers = ["😒", "🤓", "😎", "😬", "😯", "😶"]
correct_sticker = {}
captcha_checked = {}


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
        await message.answer("Error creating user. Please try again three times.")
        return

    if await has_passed_captcha_recently(user_id):
        await start_cmd(message)
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
            f"select the specified smiley:</strong> {correct_sticker[user_id]} \n\n"
            f"<i>After passing the captcha, you will get access to the bot</i>",
            reply_markup=keyboard,
            parse_mode="HTML",
        )


async def check_captcha(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    try:
        if not await has_passed_captcha_recently(user_id):
            if callback.data == correct_sticker.get(user_id):
                if await mark_captcha_passed(user_id, callback.data):
                    await callback.answer("Captcha passed!")
                    await callback.message.delete()
                    captcha_checked[user_id] = True
                    await start_cmd(callback.message)
                else:
                    await callback.answer(
                        "Error saving captcha status. Please try again."
                    )
            else:
                await callback.answer("Wrong sticker. Try again.")
        else:
            await start_cmd(callback.message)
    except CaptchaRecord.DoesNotExist:
        await callback.answer("An error occurred. Please try again.")
