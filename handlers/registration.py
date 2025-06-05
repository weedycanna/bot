import os
from typing import Union

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message, ReplyKeyboardRemove
from django.conf import settings
from django.utils import timezone
from phonenumbers import NumberParseException
from app_config import bot_messages
from handlers.captcha import CaptchaManager

from app import CHANNEL_LINK
from django_project.telegrambot.usersmanage.models import CaptchaRecord, Order
from filters.chat_types import ChatTypeFilter
from handlers.check_subscription import CheckSubscription
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
        if await CaptchaManager.has_passed_recently(user_id):
            await start_cmd(message)
        else:
            await CaptchaManager.send_new_captcha(message, user_id)
        return

    if not await CaptchaManager.has_passed_recently(user_id):
        await CaptchaManager.send_new_captcha(message, user_id)
        return

    await message.answer(bot_messages.get("first_name_request"))
    await state.set_state(RegistrationStates.first_name)


@registration_router.message(StateFilter(RegistrationStates.first_name))
async def process_first_name(message: types.Message, state: FSMContext):
    if len(message.text) > 30:
        await message.answer(bot_messages.get("name_too_long"))
        return

    await state.update_data(first_name=message.text)
    await state.set_state(RegistrationStates.phone)
    await message.answer(
        bot_messages.get("phone_request"),
        reply_markup=get_back_button(),
        parse_mode="HTML",
    )


@registration_router.message(StateFilter(RegistrationStates.phone))
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == bot_messages.get("back_button"):
        await state.set_state(RegistrationStates.first_name)
        await message.answer(bot_messages.get("first_name_request"), reply_markup=ReplyKeyboardRemove())
        return

    try:
        formatted_phone = format_phone_number(message.text)
        if not formatted_phone:
            await message.answer(bot_messages.get("invalid_phone_format"))
            return

        user_data = await state.get_data()

        user_id = message.from_user.id
        user = await create_telegram_user(
            user_id=user_id, first_name=user_data["first_name"], phone_number=formatted_phone
        )

        if not user:
            await message.answer(bot_messages.get("phone_already_registered"))
            return

        await state.clear()

        await message.answer(
            bot_messages.get("registration_complete_with_data", name=user_data["first_name"], phone=formatted_phone)
        )

        if await CheckSubscription.check_member_subscription(user_id):
            await start_cmd(message)
        else:
            kb = create_keyboard((bot_messages.get("check_subscription_button"), "check_subscription"))
            await message.answer(
                bot_messages.get("subscription_required", channel_link=CHANNEL_LINK),
                reply_markup=kb,
                parse_mode="Markdown",
            )

    except NumberParseException:
        await message.answer(bot_messages.get("invalid_phone_format_intl"))
    except ValueError:
        await message.answer(bot_messages.get("invalid_phone_retry"))
    except Exception:
        await message.answer(bot_messages.get("registration_error"))


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
        captcha_status_text = (
            bot_messages.get("captcha_passed")
            if (captcha_status and captcha_status.is_passed)
            else bot_messages.get("captcha_not_passed")
        )

        days_in_bot = (timezone.now() - user.created_at).days

        first_name = update.from_user.first_name or ""
        last_name = update.from_user.last_name or ""
        username = update.from_user.username or ""

        profile_text = bot_messages.get(
            "profile_text",
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone=user.phone_number,
            captcha_status=captcha_status_text,
            days_in_bot=days_in_bot,
            orders_count=len(orders),
            registration_date=user.created_at.strftime("%d.%m.%Y"),
        )

        banner = await get_banner("profile")

        if not banner:
            raise ValueError(bot_messages.get("banner_not_found"))

        if not banner.image:
            raise ValueError(bot_messages.get("banner_no_image"))

        image_path = os.path.join(settings.MEDIA_ROOT, str(banner.image))
        if not os.path.exists(image_path):
            raise FileNotFoundError(bot_messages.get("banner_image_not_found", path=image_path))

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
            bot_messages.get("profile_load_error"), show_alert=True
        )