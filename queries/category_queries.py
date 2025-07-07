from asgiref.sync import sync_to_async

from django_project.telegrambot.usersmanage.models import Category


@sync_to_async
def get_categories() -> list[Category]:
    return list(Category.objects.all())


@sync_to_async
def create_categories(categories: list[str]) -> None:
    if not Category.objects.exists():
        categories_objects = [Category(name=name) for name in categories]
        Category.objects.bulk_create(categories_objects)
