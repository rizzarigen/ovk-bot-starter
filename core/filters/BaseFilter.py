from ..types import Message

class BaseFilter:
    """Базовый фильтр. Переопредели __call__."""

    def __call__(self, message: Message) -> bool:
        raise NotImplementedError
