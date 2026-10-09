


from .types import Message, Handler
from .filters import BaseFilter
import inspect

class Processor:
    def __init__(self):
        self.commands: list[Handler] = []
        self.di: dict = {}

    def add(self, *filters: BaseFilter):
        def decorator(func):
            self.commands.append(Handler(
                name=func.__name__,
                description=func.__doc__ or "",
                handler=func,
                filters=list(filters),
            ))
            return func
        return decorator

    async def process(self, message: Message):
        for command in self.commands:
            if all(f(message) for f in command.filters):
                
                sig = inspect.signature(command.handler)
                
                kwargs = {}
                kwargs["message"] = message 
                
                for name, param in sig.parameters.items():
                    if name in self.di:
                        kwargs[name] = self.di[name]
                
                await command.handler(**kwargs)
                
                return  # первая совпавшая команда выигрывает
            
    async def add_di(self, name: str, value):
        self.di[name] = value

