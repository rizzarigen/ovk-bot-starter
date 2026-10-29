
import httpx
import asyncio

from .types import Message
from .types.uploads.PhotoUpload import PhotoUpload
from .types.responses.PhotoUploadResponse import PhotoUploadResponse
from .Processor import Processor
from .types.Photo import Photo
from .exceptions.HandleException import HandleException
import logging
from .types.system.LongPollServer import LongPollServer
from .types.system.LongPollEvent import LongPollEvent

logger = logging.getLogger(__name__)

class OvkApi:
    def __init__(
        self,
        token: str | None = None,
        id: int = None,
        base_url: str = "https://api.openvk.org",
    ):
        
        self._client = httpx.AsyncClient(base_url=base_url)
        
        if token is None:
            raise ValueError("There is not any token")

        self._token = token
        self._id = id
        self._client.headers.update({"Authorization": f"Bearer {self._token}"})
    @staticmethod
    def by_credentials(
        login: str | None = None,
        password: str | None = None,
        base_url: str | None = "https://api.openvk.org"
        ) -> "OvkApi":
        if login is None or password is None:
            raise ValueError("Give the full credentials!")
        
        authorize = OvkApi._get_authorize(
                                login,
                                password,
                                base_url
                            )
        logger.debug("Token is ready!")   
        api_instance = OvkApi(token=authorize.get("access_token"), id = authorize.get("user_id"), base_url=base_url)
       
        return api_instance
        
    @staticmethod
    def by_token(
        token: str | None = None,
        base_url: str | None = "https://api.openvk.org"
    ) -> "OvkApi":
        
        if token is None:
            raise ValueError("There is no token, just give some.")
        
        return OvkApi(token = token, base_url = base_url)
    
    @staticmethod
    def _get_authorize(login: str | None = None,
        password: str | None = None,
        base_url: str | None = "https://api.openvk.org"
        ):
        
        return httpx.get(
                    f"{base_url}/token?username={login}&password={password}&grant_type=password", timeout=10
                ).json()
        
    @property
    def id(self):
        return self._id
    
    async def _call_api(self, method: str, params: dict | None = None):
        if params is None:
            params = {}
        response = await self._client.get(f"/method/{method}", params=params)
        return response.json()
    
    async def _call_api_post(self, method: str, params: dict | None = None):
        if params is None:
            params = {}
        response = await self._client.post(f"/method/{method}", data=params)
        return response.json()


    
    async def _get_message_upload_photo_url(self, peer_id: int):
        params = {"peer_id": peer_id}
        resp = await self._call_api("photos.getMessagesUploadServer", params=params)
        resp = resp.get("response", {})
        return resp.get("upload_url")
    
    async def _upload_photo(self, peer_id: int, photo_path: str):
        
        upload_url = await self._get_message_upload_photo_url(peer_id)
        photo_upload = PhotoUpload(upload_url=upload_url, photo_path=photo_path)
        
        files = {"photo": photo_upload.photo}
        async with httpx.AsyncClient() as client:
            response = await client.post(photo_upload.upload_url, files=files)
        
        upload_response_data = response.json()
        return PhotoUploadResponse(**upload_response_data)
            
    async def _save_uploaded_photo(self, upload_response: PhotoUploadResponse):
        params = {
            "server": upload_response.server,
            "photo": upload_response.photo,
            "hash": upload_response.hash,
        }
        return await self._call_api("photos.saveMessagesPhoto", params=params)
        

    
    async def long_poll_async(self, processor: Processor):
        logger.warning("[WARN] long_poll_async() is deprecated now and will be deleted in 0.5. Use start_polling() with same arguments instead")

        await self.start_polling(processor)
            
    async def start_polling(self, processor: Processor):
        
        
        server = await LongPollServer.by_api(self)
        
        async with server as s:
            while True:
                try:
                    async for event in s.get_updates():
                        await processor.process_event(event=event, api = self)
                            
                except httpx.TimeoutException:
                    continue
                except Exception as e:
                    logger.error("[ERROR] ", e.__cause__, e.__context__)
                    
            

    async def send_message(self, peer_id: int, message: str, reply_to: int | None = None, photo: Photo = None):
        params = {"peer_id": peer_id, "message": message, "reply_to": reply_to}
        
        if photo is not None:
            upload_response = await self._upload_photo(peer_id, photo.path)
            saved_photos = await self._save_uploaded_photo(upload_response)
        
            if not saved_photos.get("response"):
                raise Exception("Failed to save uploaded photo")

            photo_info = saved_photos["response"][0]
            attachment = f"photo{photo_info['owner_id']}_{photo_info['id']}_{photo_info['access_key'] if 'access_key' in photo_info else ''}"
            params["attachment"] = attachment
            
            
        return await self._call_api_post("messages.send", params=params)
    
    async def send_photo(self, peer_id: int, photo_path: str, message: str = ""):
        print("[WARN] send_photo is deprecated and will be removed. Use send_message with Photo() object witth photo= kwarg instead")    
        
        upload_response = await self._upload_photo(peer_id, photo_path)
        saved_photos = await self._save_uploaded_photo(upload_response)
        
        if not saved_photos.get("response"):
            raise Exception("Failed to save uploaded photo")
        
        photo_info = saved_photos["response"][0]
        attachment = f"photo{photo_info['owner_id']}_{photo_info['id']}_{photo_info['access_key'] if 'access_key' in photo_info else ''}"
        
        params = {"peer_id": peer_id, "message": message, "attachment": attachment}
        return await self._call_api_post("messages.send", params=params)

    async def get_user_info(self, user_id: int):
        params = {"user_ids": user_id}
        return await self._call_api("users.get", params=params)
         