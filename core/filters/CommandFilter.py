from .BaseFilter import BaseFilter
from ..types import Message

class Command(BaseFilter):
    """Проверяет, что сообщение начинается с `prefix + name` (и опционально — аргументы после)."""

    def __init__(
        self,
        prefix: str,
        name: str,
        *,
        case_sensitive: bool = False,
        allow_args: bool = True,
    ):
        self.prefix = prefix
        self.name = name
        self.case_sensitive = case_sensitive
        self.allow_args = allow_args

    def __call__(self, message: Message) -> bool:
        if not message.text:
            return False

        text = message.text if self.case_sensitive else message.text.lower()
        prefix = self.prefix if self.case_sensitive else self.prefix.lower()
        name = self.name if self.case_sensitive else self.name.lower()

        if not text.startswith(prefix + name):
            return False

        if self.allow_args:
            rest = text[len(prefix) + len(name):]
            return rest == "" or rest.startswith(" ")

        return text == prefix + name