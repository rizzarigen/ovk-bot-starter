from .BaseFilter import BaseFilter
from ..types import Message

class Command(BaseFilter):
    """Проверяет, что сообщение начинается с `prefix + name` (и опционально — аргументы после)."""

    def __init__(
        self,
        prefix: str,
        name: str,
        req_args: list = None,
        *,
        case_sensitive: bool = False,
    ):
        self.prefix = prefix
        self.name = name
        self.case_sensitive = case_sensitive
        self.req_args = req_args

    def __call__(self, message: Message) -> bool:
        if not message.text:
            return False

        text = message.text if self.case_sensitive else message.text.lower()
        prefix = self.prefix if self.case_sensitive else self.prefix.lower()
        name = self.name if self.case_sensitive else self.name.lower()
        

        if not text.startswith(prefix + name):
            return False

        if self.req_args is not None:
            rest = text[len(prefix) + len(name) + 1:]
            if len(rest.split(" ")) < len(self.req_args):
                raise Exception("Аргументы команды не указаны или указаны не полностью")
            return rest == "" or len(rest) > 0

        return text == prefix + name