

from typing import Awaitable, Callable
from .Message import Message
from ..filters.CommandFilter import Command
import inspect

from pydantic import BaseModel, ConfigDict

class Handler(BaseModel):
    name: str
    description: str
    func: Callable[..., Awaitable[None]]
    filters: list = []
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    async def is_match(self, message: Message) -> bool:        
        for filter in self.filters:
            if filter(message):
                continue
            else:
                return False
        return True
    
    
    ### TODO: refactor
    async def build_kwargs(self, di: dict):
        sig = inspect.signature(self.func)
        kwargs = {}
        for key in sig.parameters.keys():
            if key in di:
                kwargs[key] = di[key]                
        return kwargs
    
    async def _parse_args(self, msg: Message):
        for f in self.filters:
            kwargs = {}
            if isinstance(f, Command) and isinstance(f.req_args, list):
                required_args_count = len(f.req_args)
                args = msg.text.split(" ")[1:]
                
                        
                parsed_req_args = args[:required_args_count]
                print(parsed_req_args)
                
                for i in range(required_args_count):

                    print(parsed_req_args)
                    kwargs[f.req_args[i]] = parsed_req_args[i]
                    
                if len(args) > len(parsed_req_args):
                    tail = " ".join(args[required_args_count:])
                    kwargs["tail"] = tail
                
                print(kwargs)
            return kwargs
    
    async def handle(self, msg: Message, di: dict):
        kwargs = await self.build_kwargs(di) | await self._parse_args(msg)
        kwargs["message"] = msg
        await self.func(**kwargs)