

from pydantic import BaseModel, PrivateAttr, computed_field
from .system.LongPollEvent import LongPollEvent

class Message(BaseModel):
    id: int | None = None
    peer_id: int | None = None
    ts: int | None = None
    text: str | None = None
    extra_fields: dict | None = None
    
    _api: "OvkApi" = PrivateAttr(default=None)
    
    def bind_api(self, api: any):
        self._api = api
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
    
    @staticmethod
    async def by_event(event: "LongPollEvent"):
        return Message(
                        id = event.message_id,
                        peer_id= event.peer_id,
                        ts=event.timestamp,
                        text = event.text,
                        extra_fields=event.extra_fields
                        )
        
        

        
