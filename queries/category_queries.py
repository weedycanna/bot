from typing import List

from asgiref.sync import sync_to_async

from django_project.telegrambot.usersmanage.models import Category


@sync_to_async
def get_categories() -> List[Category]:
    return list(Category.objects.all())


@sync_to_async
def create_categories(categories: List[str]) -> None:
    if not Category.objects.exists():
        categories_objects = [Category(name=name) for name in categories]
        Category.objects.bulk_create(categories_objects)
