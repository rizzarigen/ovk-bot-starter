from ...OvkApi import OvkApi
import logging
from httpx import AsyncClient, TimeoutException, RequestError
from .LongPollEvent import LongPollEvent
import asyncio

logger = logging.getLogger(__name__)


class LongPollServer:
    def __init__(self, url, key, ts, api):
        self.url: str = url
        self.key: str = key
        self.ts:  str = ts
        self.api: "OvkApi" = api
        
        self._wait: int = 25
        self._version: int = 3
        self._mode = 2
        
    @staticmethod
    async def by_api(api: "OvkApi"):
        resp = await api._call_api("messages.getLongPollServer")
        resp = resp.get("response", {})
    
        ts = resp.get("ts")
        key = resp.get("key")
        url = resp.get("server")
        return LongPollServer(url, key, ts)
    
    @property
    async def _request_parameters(self):
        return {"wait": 25, 
                "key": self.key, 
                "version": self._version, 
                "act": "a_check", "ts": self.ts, 
                "mode": self._mode}
    
    async def send_longpoll_request(self) -> list[LongPollEvent]:
        async with AsyncClient as client:
            try:
                response = await client.get(self.url,
                                            params = self._request_parameters,
                                            timeout = 30
                                            )
                if response.status_code == 200:
                    data = response.json()
                    
                    result = []
                    
                    updates = data.get("updates", [])
                     
                    for update in updates:
                        result.append(
                            LongPollEvent(update)
                            )
                    return result
            except TimeoutException as e:
                raise e
            except RequestError:
                logger.error(f"Ошибка запроса: {e}")
                await asyncio.sleep(5)
    
    