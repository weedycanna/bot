from asgiref.sync import sync_to_async

from django_project.telegrambot.usersmanage.models import TelegramUser


@sync_to_async
def get_user_language(user_id: int) -> str:
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        return user.language
    except TelegramUser.DoesNotExist:
        return "en"


@sync_to_async
def set_user_language(user_id: int, language: str) -> bool:
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        user.language = language
        user.save()
        return True
    except TelegramUser.DoesNotExist:
        return False


@sync_to_async
def get_or_create_user_language(user_id: int, default_language: str = "en") -> str:
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        return user.language
    except TelegramUser.DoesNotExist:
        return default_language
