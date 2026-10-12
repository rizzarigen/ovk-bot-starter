


from .types import Message, Handler
from .filters import BaseFilter, Command
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
            matched = [f for f in command.filters if f(message)]
            
            if len(matched) == len(command.filters):  # все фильтры сработали
                # matched — список сработавших фильтров
                
                sig = inspect.signature(command.handler)
                kwargs = {"message": message}
                
                arg_names = sig.parameters.keys()

                        
                for f in matched:
                    if isinstance(f, Command) and isinstance(message.args, list):

                        args = message.args
                        args_count = len(f.req_args)
                        message = message.set_required_args_count(args_count)
                        for i in range(args_count):
                            kwargs[f.req_args[i]] = args[i]
                            
                for name in arg_names:
                    if name in self.di:
                        kwargs[name] = self.di[name]
                
                await command.handler(**kwargs)
                return
            
    async def add_di(self, name: str, value):
        self.di[name] = value

