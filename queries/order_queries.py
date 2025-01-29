from typing import List

from asgiref.sync import sync_to_async
from django.db import transaction

from django_project.telegrambot.usersmanage.models import (
    Cart,
    Order,
    OrderItem,
    TelegramUser,
)


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


@sync_to_async
def add_order_with_items(
    user_id: int,
    name: str,
    phone: str,
    address: str,
    status: str,
    cart_items: List[Cart],
) -> Order:
    user = TelegramUser.objects.get(user_id=user_id)
    try:
        with transaction.atomic():
            order = Order.objects.create(
                user=user, name=name, phone=phone, address=address, status=status
            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                )

            return order
    except (OrderItem.DoesNotExist, Order.DoesNotExist):
        raise


@sync_to_async
def get_order_by_id(order_id: str) -> Order:
    return Order.objects.filter(id=order_id).first()


@sync_to_async
def get_order_items(order_id: str) -> List[OrderItem]:
    items = list(
        OrderItem.objects.filter(order_id=order_id).select_related("product").all()
    )
    return items


@sync_to_async
def total_orders() -> int:
    return Order.objects.count()


@sync_to_async
def get_order_status(order_id: str) -> str:
    try:
        order = Order.objects.get(id=order_id)
        return order.status
    except Order.DoesNotExist:
        return "unknown"