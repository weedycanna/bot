import json
import logging
import os
from typing import Dict, Any, Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

logger = logging.getLogger(__name__)


class EnvConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    TOKEN: str
    CHANNEL_ID: str
    CHANNEL_LINK: str

    CRYPTO_TOKEN: str
    STAR_PAYMENT_TOKEN: str

    DELETE_ANIMATION_URL: str = "https://media.giphy.com/media/h3oEjI6SIIHBdRxXI40/giphy.gif"

    ADMIN_LIST: str = Field(default="", alias="ADMIN_LIST")

    @property
    def ADMIN_USER_LIST(self) -> List[int]:
        if not self.ADMIN_LIST:
            return []
        try:
            return [int(admin_id) for admin_id in self.ADMIN_LIST.split(",") if admin_id.strip()]
        except ValueError:
            logger.error("ADMIN_USER_IDS in .env is not a valid list of integers.")
            return []


env_config = EnvConfig()


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    DJANGO_SUPERUSER_USERNAME: str = "test"
    DJANGO_SUPERUSER_EMAIL: str = "test@gmail.com"
    DJANGO_SUPERUSER_PASSWORD: str = "test123!"


db_config = DatabaseConfig()


class BotMessages:
    def __init__(self, messages_file="data/bot_messages.json"):
        self.messages_file = messages_file
        self._messages = self._load_messages()

    def _load_messages(self) -> Dict[str, Any]:
        if os.path.exists(self.messages_file):
            try:
                with open(self.messages_file, 'r', encoding='utf-8') as f:
                    loaded_messages = json.load(f)
                return loaded_messages
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load messages from {self.messages_file}. Error: {e}")
                return {}
        else:
            os.makedirs(os.path.dirname(self.messages_file), exist_ok=True)
            empty_messages = {}
            self._save_messages(empty_messages)
            return empty_messages

    def _save_messages(self, messages_to_save: Optional[Dict[str, Any]] = None) -> None:
        _messages_to_save = messages_to_save if messages_to_save is not None else self._messages

        os.makedirs(os.path.dirname(self.messages_file), exist_ok=True)
        try:
            with open(self.messages_file, 'w', encoding='utf-8') as f:
                json.dump(_messages_to_save, f, ensure_ascii=False, indent=4)
        except IOError as e:
            logger.error(f"Failed to save messages to {self.messages_file}. Error: {e}")

    def get(self, key: str, default: Optional[Any] = None, **kwargs) -> Any:
        message = self._messages.get(key, default if default is not None else f"Message '{key}' not found.")

        if kwargs and message:
            try:
                message = message.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing formatting argument in message '{key}': {e}")

        return message

    def set(self, key: str, value: Any) -> None:
        self._messages[key] = value
        self._save_messages()

    def __getattr__(self, name: str) -> Any:
        if name in self._messages:
            return self._messages[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def get_all_messages(self) -> Dict[str, Any]:
        return self._messages.copy()


bot_messages = BotMessages()
