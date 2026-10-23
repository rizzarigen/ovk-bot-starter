


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
                handler=func,
                filters=list(filters),
            ))
            return func
        return decorator
    

    async def _process_message(self, message: Message):
        for handler in self.handlers:
            matched = [f for f in handler.filters if f(message)]
            
            if await handler.is_match(message):  
                print("MATCHED!")
                sig = inspect.signature(handler.handler)
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
                
                await handler.handler(**kwargs)
                return
            
    async def process_event(self, event: LongPollEvent, api: "OvkApi"):        
        if event.type_code == 4:
            msg = await Message.by_event(event)
            msg.bind_api(api)
            await self._process_message(msg)
        
    async def add_di(self, name: str, value):
        self.di[name] = value

