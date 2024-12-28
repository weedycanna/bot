from typing import List

from asgiref.sync import sync_to_async

from django_project.telegrambot.usersmanage.models import Order, TelegramUser


@sync_to_async
def get_user_orders(user_id: int) -> List[Order]:
    user = TelegramUser.objects.get(user_id=user_id)
    return list(Order.objects.filter(user=user).order_by("-created_at"))


@sync_to_async
def add_order(
    user_id: int, name: str, phone: str, address: str, status: str = "pending"
) -> Order | None:
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        order = Order.objects.create(
            user=user, name=name, phone=phone, address=address, status=status
        )
        return order
    except Order.DoesNotExist:
        return None
