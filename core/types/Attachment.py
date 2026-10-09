from pydantic import BaseModel

class Attachment(BaseModel):
    type: str
    id: int