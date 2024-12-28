from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils import timezone

from django_project.telegrambot.usersmanage.models import (CaptchaRecord,
                                                           TelegramUser)
from queries.user_queries import get_user


@sync_to_async
def mark_captcha_passed(user_id: int, selected_sticker: str) -> bool:
    try:
        with transaction.atomic():
            user = TelegramUser.objects.select_for_update().get(user_id=user_id)

            CaptchaRecord.objects.filter(user=user).delete()

            CaptchaRecord.objects.create(
                user=user,
                captcha=selected_sticker,
                timestamp=timezone.now(),
                is_passed=True,
            )
            return True
    except TelegramUser.DoesNotExist:
        return False


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
