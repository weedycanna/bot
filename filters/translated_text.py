from aiogram.filters import Filter
from aiogram.types import Message
from fluentogram import TranslatorRunner


class TranslatedText(Filter):
    def __init__(self, key: str):
        self.key = key

    async def __call__(self, message: Message, i18n: TranslatorRunner) -> bool:
        translated_text = i18n.get(self.key)

        return message.text == translated_text
