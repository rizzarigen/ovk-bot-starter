

from typing import Awaitable, Callable

from pydantic import BaseModel, ConfigDict

class Handler(BaseModel):
    name: str
    description: str
    handler: Callable[..., Awaitable[None]]
    filters: list = []
    model_config = ConfigDict(arbitrary_types_allowed=True)
