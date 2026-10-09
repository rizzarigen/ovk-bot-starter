from pydantic import BaseModel

class UploadServer(BaseModel):
    upload_url: str