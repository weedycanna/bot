from typing import List, Optional

from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import F

from django_project.telegrambot.usersmanage.models import Cart, TelegramUser


@sync_to_async
def add_to_cart(user_id: int, product_id: int) -> Optional[Cart]:
    try:
        with transaction.atomic():
            user = TelegramUser.objects.get(user_id=user_id)

            cart_item, created = Cart.objects.get_or_create(
                user=user, product_id=product_id, defaults={"quantity": 1}
            )

            if not created:
                cart_item.quantity = F("quantity") + 1
                cart_item.save()

            cart_item.refresh_from_db()
            return cart_item
    except TelegramUser.DoesNotExist:
        return None
    except Cart.DoesNotExist:
        return None


@sync_to_async
def get_cart_items(user_id: int) -> List[Cart]:
    return list(
        Cart.objects.filter(user__user_id=user_id).select_related("product").all()
    )


@sync_to_async
def get_user_carts(user_id: int) -> List[Cart]:
    user = TelegramUser.objects.get(user_id=user_id)
    return list(Cart.objects.filter(user=user).select_related("product"))


@sync_to_async
def delete_from_cart(user_id: int, product_id: int) -> None:
    user = TelegramUser.objects.get(user_id=user_id)
    Cart.objects.filter(user=user, product_id=product_id).delete()


@sync_to_async
def clear_cart(user_id: int) -> None:
    user = TelegramUser.objects.get(user_id=user_id)
    Cart.objects.filter(user=user).delete()


@sync_to_async
def reduce_product_in_cart(user_id: int, product_id: int) -> bool:
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        cart_item = Cart.objects.get(user=user, product_id=product_id)

        if cart_item.quantity > 1:
            cart_item.quantity = F("quantity") - 1
            cart_item.save()
            return True
        else:
            cart_item.delete()
            return False
    except Cart.DoesNotExist:
        return False

