import os

from aiogram.types import FSInputFile, InputMediaPhoto
from django.conf import settings
from fluentogram import TranslatorRunner

from queries.banner_queries import get_banner


async def get_banner_image(menu_name: str, i18n: TranslatorRunner) -> InputMediaPhoto:
    banner = await get_banner(menu_name)

    if not (banner and banner.image):
        raise ValueError(i18n.banner_not_found_or_no_image())

    image_path = os.path.join(settings.MEDIA_ROOT, str(banner.image))
    if not os.path.exists(image_path):
        raise FileNotFoundError(i18n.banner_image_not_found(path=image_path))

    return InputMediaPhoto(
        media=FSInputFile(image_path),
        caption=str(banner.description) if banner.description else ""
    )
