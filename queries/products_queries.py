from typing import Dict, List, Optional

from asgiref.sync import sync_to_async

from django_project.telegrambot.usersmanage.models import Category, Product


@sync_to_async
def add_product(data: Dict) -> None:
    Product.objects.create(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"]),
    )


@sync_to_async
def get_products(category_id: Optional[int] = None) -> List[Product]:
    try:
        if category_id is not None:
            products = Product.objects.filter(category_id=int(category_id))
        else:
            products = Product.objects.all()
        return list(products)
    except Product.DoesNotExist:
        return []


@sync_to_async
def get_product(product_id: int) -> Optional[Product]:
    return Product.objects.filter(id=product_id).first()


@sync_to_async
def update_product(product_id: int, data: Dict) -> None:
    Product.objects.filter(id=product_id).update(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"]),
    )


@sync_to_async
def delete_product(product_id: int) -> None:
    Product.objects.filter(id=product_id).delete()


@sync_to_async
def total_products() -> int:
    return Product.objects.count()


@sync_to_async
def total_products_by_category() -> dict[str, int]:
    categories = Category.objects.all()
    category_stats = {}
    for category in categories:
        category_stats[category.name] = Product.objects.filter(
            category_id=category.id
        ).count()
    return category_stats
