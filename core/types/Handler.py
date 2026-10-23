

from typing import Awaitable, Callable
from .Message import Message

from pydantic import BaseModel, ConfigDict

class Handler(BaseModel):
    name: str
    description: str
    handler: Callable[..., Awaitable[None]]
    filters: list = []
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    async def is_match(self, message: Message) -> bool:        
        for filter in self.filters:
            if filter(message):
                continue
            else:
                return False
        return True