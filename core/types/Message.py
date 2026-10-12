

from pydantic import BaseModel, PrivateAttr, computed_field

class Message(BaseModel):
    id: int | None = None
    peer_id: int | None = None
    ts: int | None = None
    text: str | None = None
    extra_fields: dict | None = None
    
    _api: "OvkApi" = PrivateAttr(default=None)
    _req_args_count = PrivateAttr(default=None)
    
    def bind_api(self, api: any):
        self._api = api
        return self
    
    def set_required_args_count(self, value: int):
        self._req_args_count = value
        return self
    
    async def answer(self, text: str = None, photo: "Photo" = None):
        return await self._api.send_message(
            peer_id = self.peer_id,
            message = text,
            photo = photo
        )
        
    async def reply (self, text: str, photo: "Photo" = None):
        return await self._api.send_message(
            peer_id = self.peer_id,
            message = text,
            reply_to = self.id,
            photo = photo
        )
        
    @computed_field(return_type=None|list)
    def args(self):
        
        args = self.text.split(" ")
        
        req_args = args[1:self._req_args_count]
        
        
        if len(req_args) > 0:
            return req_args
        else:
            return None

    @computed_field(return_type=str|None)
    def args_rest(self):
        args = self.text.split(" ")
        tail = args[self._req_args_count + 1:]
        return " ".join(tail)
        
