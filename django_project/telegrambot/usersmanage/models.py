import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

ORDER_STATUS = (
    ("pending", "pending"),
    ("completed", "completed"),
    ("cancelled", "cancelled"),
)

LANGUAGE = (
    ("en", "English"),
    ("ru", "Russian"),
)


class TimeBasedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Banner(TimeBasedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25, unique=True)
    image = models.ImageField(upload_to="banners", blank=True, null=True)
    description = models.TextField(max_length=1024, blank=True, null=True)

    class Meta:
        verbose_name_plural: str = "Banners"
        verbose_name: str = "Banner"

    def __str__(self):
        return f"Banner {self.name}"


class Category(TimeBasedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural: str = "Categories"
        verbose_name: str = "Category"

    def __str__(self):
        return f"{self.name}"


class Product(TimeBasedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    description = models.TextField(max_length=1024)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to="products", blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )

    class Meta:
        verbose_name_plural: str = "Products"
        verbose_name: str = "Product"

    def __str__(self):
        return f"{self.name}"


class AdminUser(AbstractUser):
    USERNAME_FIELD = "username"

    def __str__(self):
        return f"{self.username}"


class TelegramUser(TimeBasedModel):
    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(_("first name"), max_length=30)
    phone_number = PhoneNumberField(_("phone number"), unique=True)
    language = models.CharField(
        _("language"), max_length=10, choices=LANGUAGE, default="en"
    )

    class Meta:
        verbose_name = _("Telegram User")
        verbose_name_plural = _("Telegram Users")
        ordering = ("first_name",)
        indexes = [
            models.Index(fields=["first_name", "phone_number"]),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name}".strip()


class Cart(TimeBasedModel):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="cart"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart")
    quantity = models.IntegerField()

    class Meta:
        verbose_name_plural: str = "Carts"
        verbose_name: str = "Cart"

    def __str__(self):
        return f"<Cart {self.user_id} {self.product_id}>"


class Order(TimeBasedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="orders"
    )
    name = models.CharField(max_length=150)
    address = models.TextField()
    phone = PhoneNumberField()
    status = models.CharField(max_length=25, choices=ORDER_STATUS, default="pending")

    class Meta:
        verbose_name_plural: str = "Orders"
        verbose_name: str = "Order"

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(TimeBasedModel):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        verbose_name_plural: str = "Order Items"
        verbose_name: str = "Order Item"

    def __str__(self):
        return (
            f"OrderItem {self.id} - Order {self.order.id} - Product {self.product.name}"
        )


class CaptchaRecord(TimeBasedModel):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="captchas"
    )
    captcha = models.CharField(max_length=50)
    timestamp = models.DateTimeField(default=timezone.now)
    is_passed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user",)
        verbose_name_plural: str = "Captcha"
        verbose_name: str = "Captcha"

    def __str__(self):
        return f"Captcha {self.id} - User {self.user.id}"
