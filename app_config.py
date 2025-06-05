import json
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

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
