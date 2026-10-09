from pydantic import BaseModel, computed_field

class PhotoUpload(BaseModel):
    upload_url: str
    hash: str = None
    photo_path: str = None
    
    @computed_field
    @property
    def photo(self) -> bytes:
        if self.photo_path is None:
            raise ValueError("photo_path must be set before accessing photo")
        with open(self.photo_path, "rb") as f:
            return f.read()