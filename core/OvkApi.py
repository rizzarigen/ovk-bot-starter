
import httpx
import asyncio

from .types import Message
from .types.uploads.PhotoUpload import PhotoUpload
from .types.responses.PhotoUploadResponse import PhotoUploadResponse
from .Processor import Processor

class OvkApi:
    def __init__(
        self,
        token: str | None = None,
        login: str | None = None,
        password: str | None = None,
        base_url: str = "https://api.openvk.org",
    ):
        self._client = httpx.AsyncClient(base_url=base_url)

        if token is None and login is None and password is None:
            raise Exception("хоть че нить дай, как я войду бляь?")
        elif (login is None or password is None) and token is None:
            raise Exception("Ну ты бля креденшлы дай, крендель ебана")

        self._token = token if token is not None else httpx.get(
            f"{base_url}/token?username={login}&password={password}&grant_type=password"
        ).json().get("access_token")

        self._client.headers.update({"Authorization": f"Bearer {self._token}"})

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

    async def _get_long_poll_server(self):
        resp = await self._call_api("messages.getLongPollServer")
        resp = resp.get("response", {})
        ts = resp.get("ts")
        key = resp.get("key")
        url = resp.get("server")
        return url, key, ts
    
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
        url, key, ts = await self._get_long_poll_server()

        url = url if url.startswith("http") else f"https://{url}"

        params = {"wait": 25, "key": key, "version": 3, "act": "a_check", "ts": ts, "mode": 2}
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    response = await client.get(url, params=params, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        
                        for update in data.get("updates", []):
                            if update[0] == 4 and len(update) >= 7:
                                msg = Message(
                                    id=update[1],
                                    peer_id=update[3],
                                    ts=update[4],
                                    text=update[6],
                                    extra_fields=update[7] if len(update) > 7 and isinstance(update[7], dict) else {},
                                )
                                await processor.process(msg)

                        params["ts"] = data.get("ts")
                except httpx.TimeoutException:
                    continue
                except httpx.RequestError as e:
                    print(f"Ошибка запроса: {e}")
                    await asyncio.sleep(5)

    async def send_message(self, peer_id: int, message: str, reply_to: int | None = None):
        params = {"peer_id": peer_id, "message": message, "reply_to": reply_to}
        return await self._call_api_post("messages.send", params=params)
    
    async def send_photo(self, peer_id: int, photo_path: str, message: str = ""):
        upload_response = await self._upload_photo(peer_id, photo_path)
        saved_photos = await self._save_uploaded_photo(upload_response)
        
        if not saved_photos.get("response"):
            raise Exception("Failed to save uploaded photo")
        
        photo_info = saved_photos["response"][0]
        attachment = f"photo{photo_info['owner_id']}_{photo_info['id']}_{photo_info['access_key'] if 'access_key' in photo_info else ''}"
        print(attachment)
        
        params = {"peer_id": peer_id, "message": message, "attachment": attachment}
        return await self._call_api_post("messages.send", params=params)

    async def get_user_info(self, user_id: int):
        params = {"user_ids": user_id}
        return await self._call_api("users.get", params=params)
         