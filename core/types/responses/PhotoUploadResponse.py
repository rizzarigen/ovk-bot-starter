from pydantic import BaseModel

class PhotoUploadResponse(BaseModel):
    server: int
    photo: str
    hash: str