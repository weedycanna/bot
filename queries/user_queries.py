from typing import Optional

from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import Q

from django_project.telegrambot.usersmanage.models import TelegramUser
from utils.utils import format_phone_number


@sync_to_async
def create_telegram_user(
    phone_number: str, first_name: str, user_id: int
) -> Optional[TelegramUser]:
    try:
        formatted_phone = format_phone_number(phone_number)
        if not formatted_phone:
            return None

        existing_user = TelegramUser.objects.filter(
            Q(phone_number=formatted_phone) | Q(user_id=user_id)
        ).first()

        if existing_user:
            return None

        user = TelegramUser.objects.create(
            user_id=user_id,
            phone_number=formatted_phone,
            first_name=first_name,
        )
        return user

    except IntegrityError:
        return None


@sync_to_async
def add_user(
    user_id: int, first_name: str, last_name: str, phone: str = None
) -> Optional[TelegramUser]:
    try:
        user, created = TelegramUser.objects.get_or_create(
            user_id=user_id,
            defaults={
                "first_name": first_name or "",
                "last_name": last_name or "",
                "phone_number": phone or "",
            },
        )
        return user
    except IntegrityError:
        return None


@sync_to_async
def get_user(user_id: int) -> TelegramUser | None:
    try:
        return TelegramUser.objects.get(user_id=user_id)
    except TelegramUser.DoesNotExist:
        return None


@sync_to_async
def total_users() -> int:
    return TelegramUser.objects.count()