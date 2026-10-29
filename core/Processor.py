


from .types import Message, Handler
from .filters import BaseFilter, Command
import inspect
from .types.system.LongPollEvent import LongPollEvent

class Processor:
    def __init__(self):
        self.handlers: list[Handler] = []
        self.di: dict = {}

    def add(self, *filters: BaseFilter):
        def decorator(func):
            self.handlers.append(Handler(
                name=func.__name__,
                description=func.__doc__ or "",
                func=func,
                filters=list(filters),
            ))
            return func
        return decorator
    

    async def _process_message(self, message: Message):
        for handler in self.handlers:
            if await handler.is_match(message):  
                await handler.handle(message, self.di)
                return
            
    async def process_event(self, event: LongPollEvent, api: "OvkApi"):        
        if event.type_code == 4:
            msg = await Message.by_event(event) 
            msg.bind_api(api)
            return await self._process_message(msg) if msg.extra_fields.get("from") != api.id else None
        
    async def add_di(self, name: str, value):
        self.di[name] = value

