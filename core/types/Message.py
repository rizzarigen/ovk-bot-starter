

from pydantic import BaseModel

class Message(BaseModel):
    id: int | None = None
    peer_id: int | None = None
    ts: int | None = None
    text: str | None = None
    extra_fields: dict | None = None

