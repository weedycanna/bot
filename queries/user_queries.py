from typing import Optional, Union

from asgiref.sync import sync_to_async
from django.db import IntegrityError, transaction

from django_project.telegrambot.usersmanage.models import TelegramUser


@sync_to_async
def create_telegram_user(user_id: int, first_name: str, phone_number: str):
    try:
        with transaction.atomic():
            if TelegramUser.objects.filter(phone_number=phone_number).exclude(user_id=user_id).exists():
                return None

            user = TelegramUser.objects.filter(user_id=user_id).first()

            if user:
                user.first_name = first_name
                user.phone_number = phone_number
                user.save()
            else:
                user = TelegramUser.objects.create(
                    user_id=user_id,
                    first_name=first_name,
                    phone_number=phone_number
                )

            return user

    except TelegramUser.DoesNotExist:
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
