from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update
from fluentogram import TranslatorHub

from queries.language_queries import get_or_create_user_language


class I18nMiddleware(BaseMiddleware):
    def __init__(self, translator_hub: TranslatorHub):
        self.translator_hub = translator_hub

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        user = None
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user
        elif event.inline_query:
            user = event.inline_query.from_user
        if user:
            user_language = await get_or_create_user_language(user.id)
            i18n = self.translator_hub.get_translator_by_locale(user_language)
            data["i18n"] = i18n
            data["translator_hub"] = self.translator_hub
        else:
            data["i18n"] = self.translator_hub.get_translator_by_locale(
                self.translator_hub.root_locale
            )
            data["translator_hub"] = self.translator_hub

        return await handler(event, data)
