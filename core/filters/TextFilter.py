from .BaseFilter import BaseFilter
from ..types import Message

class Text(BaseFilter):
    """Проверяет, что текст сообщения равен строке (case-insensitive по умолчанию)."""

    def __init__(self, text: str, *, case_sensitive: bool = False):
        self.text = text
        self.case_sensitive = case_sensitive

    def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        if self.case_sensitive:
            return message.text == self.text
        return message.text.lower() == self.text.lower()