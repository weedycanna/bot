from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils import timezone

from django_project.telegrambot.usersmanage.models import (CaptchaRecord,
                                                           TelegramUser)


@sync_to_async
def mark_captcha_passed(user_id: int, selected_sticker: str) -> bool:
    try:
        with transaction.atomic():
            user = TelegramUser.objects.get_or_create(user_id=user_id)[0]
            CaptchaRecord.objects.create(
                user=user,
                captcha=selected_sticker,
                timestamp=timezone.now(),
                is_passed=True
            )
            return True
    except CaptchaRecord.DoesNotExist:
        return False
