import random
from typing import Any, Tuple, List, Dict

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from django.utils import timezone
from app_config import bot_messages


from app import CHANNEL_LINK
from django_project.telegrambot.usersmanage.models import CaptchaRecord
from filters.chat_types import ChatTypeFilter
from handlers.check_subscription import CheckSubscription
from handlers.start_cmd import start_cmd
from keybords.reply import create_keyboard
from queries.captcha_queries import mark_captcha_passed
from queries.user_queries import get_user
from states.registration_state import RegistrationStates
from aiogram.types import CallbackQuery

captcha_router = Router()
captcha_router.message.filter(ChatTypeFilter(["private"]))


CAPTCHA_OPTIONS: List[Tuple[str, str]] = [
    ("apple", "🍎"),
    ("car", "🚗"),
    ("candy", "🍬"),
    ("ball", "⚽"),
    ("chair", "🪑"),
    ("watch", "⌚"),
]

WORDS_TO_EMOJI: Dict[str, str] = {word: emoji for word, emoji in CAPTCHA_OPTIONS}
EMOJI_LIST: List[str] = [emoji for _, emoji in CAPTCHA_OPTIONS]
WORDS_LIST: List[str] = [word for word, _ in CAPTCHA_OPTIONS]

user_captcha_data: Dict[int, Dict[str, Any]] = {}


class CaptchaManager:

    @staticmethod
    async def has_passed_recently(user_id: int) -> bool:

        try:
            time_expiration = timezone.now() - timezone.timedelta(weeks=2)
            user = await get_user(user_id)
            if not user:
                return False

            return await sync_to_async(CaptchaRecord.objects.filter(user=user, timestamp__gt=time_expiration).exists)()
        except CaptchaRecord.DoesNotExist:
            return False

    @staticmethod
    def generate_captcha() -> Tuple[str, str, InlineKeyboardMarkup]:

        selected_word = random.choice(WORDS_LIST)
        correct_emoji = WORDS_TO_EMOJI[selected_word]

        shuffled_emojis = EMOJI_LIST.copy()
        random.shuffle(shuffled_emojis)

        buttons = [InlineKeyboardButton(text=emoji, callback_data=emoji) for emoji in shuffled_emojis]
        rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

        return selected_word, correct_emoji, keyboard

    @staticmethod
    def get_captcha_text(word: str) -> str:

        return bot_messages.get("captcha_text", word=word)

    @staticmethod
    async def send_new_captcha(message: Message, user_id: int) -> None:
        word, emoji, keyboard = CaptchaManager.generate_captcha()

        user_captcha_data[user_id] = {
            "word": word,
            "correct_emoji": emoji,
        }

        await message.answer(
            CaptchaManager.get_captcha_text(word),
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    @staticmethod
    async def regenerate_captcha(callback: types.CallbackQuery, user_id: int) -> None:

        word, emoji, keyboard = CaptchaManager.generate_captcha()

        user_captcha_data[user_id] = {
            "word": word,
            "correct_emoji": emoji,
        }

        await callback.message.edit_text(
            CaptchaManager.get_captcha_text(word),
            reply_markup=keyboard,
            parse_mode="HTML",
        )


async def handle_successful_captcha(callback: CallbackQuery, state: FSMContext, user_id: int) -> None:

    await callback.answer(bot_messages.get("captcha_success"))
    await callback.message.delete()

    if user_id in user_captcha_data:
        del user_captcha_data[user_id]

    user = await get_user(user_id)
    if user and user.phone_number:
        if await CheckSubscription.check_member_subscription(user_id):
            await start_cmd(callback.message)
        else:
            kb = create_keyboard((bot_messages.get("check_subscription_button"), "check_subscription"))
            await callback.message.answer(
                bot_messages.get("subscription_required", channel_link=CHANNEL_LINK),
                reply_markup=kb,
                parse_mode="Markdown",
            )
    else:
        await state.set_state(RegistrationStates.first_name)
        await callback.message.answer(
            bot_messages.get("welcome_message"),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )


@captcha_router.message(CommandStart())
async def captcha_cmd(message: types.Message):

    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user or user is None:
        await message.answer(bot_messages.get("user_creation_error"))
        return

    if await CaptchaManager.has_passed_recently(user_id):
        if await CheckSubscription.check_member_subscription(user_id):
            await start_cmd(message)
        else:
            kb = create_keyboard((bot_messages.get("check_subscription_button"), "check_subscription"))
            await message.answer(
                bot_messages.get("subscription_required", channel_link=CHANNEL_LINK),
                reply_markup=kb,
                parse_mode="Markdown",
            )
    else:
        await CaptchaManager.send_new_captcha(message, user_id)


@captcha_router.callback_query(lambda c: c.data in EMOJI_LIST)
async def process_captcha_callback(callback: types.CallbackQuery, state: FSMContext):

    user_id = callback.from_user.id
    selected_emoji = callback.data

    if user_id not in user_captcha_data:
        await callback.answer(bot_messages.get("captcha_expired"))
        await callback.message.delete()
        return

    correct_emoji = user_captcha_data[user_id]["correct_emoji"]
    if selected_emoji == correct_emoji:
        try:
            if await mark_captcha_passed(user_id, selected_emoji):
                await handle_successful_captcha(callback, state, user_id)
            else:
                await callback.answer(bot_messages.get("captcha_save_error"))
        except CaptchaRecord.DoesNotExist:
            await callback.answer(bot_messages.get("captcha_general_error"))
    else:
        await callback.answer(bot_messages.get("captcha_wrong_selection"))
        await CaptchaManager.regenerate_captcha(callback, user_id)