import os

from django.conf import settings


async def download_telegram_photo(message, folder, prefix) -> str:
    file = await message.bot.get_file(message.photo[-1].file_id)
    file_name = f"{prefix}.jpg"
    save_path = os.path.join(folder, file_name)
    full_path = os.path.join(settings.MEDIA_ROOT, save_path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    await message.bot.download_file(file.file_path, full_path)
    return save_path