
import asyncio
import httpx
from pydantic import BaseModel, ConfigDict
from typing import Callable, Awaitable


URL = "https://openvk.org/nim"


class Message(BaseModel):
    id: int | None = None
    peer_id: int | None = None
    ts: int | None = None
    text: str | None = None
    extra_fields: dict | None = None


class Filter:
    """Базовый фильтр. Переопредели __call__."""

    def __call__(self, message: Message) -> bool:
        raise NotImplementedError


class Text(Filter):
    """Проверяет, что текст сообщения равен строке (case-insensitive по умолчанию)."""

    def __init__(self, text: str, *, case_sensitive: bool = False):
        self.text = text
        self.case_sensitive = case_sensitive

    def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        if self.case_sensitive:
            return message.text == self.text
        return message.text.lower() == self.text.lower()


class Command(Filter):
    """Проверяет, что сообщение начинается с `prefix + name` (и опционально — аргументы после)."""

    def __init__(
        self,
        prefix: str,
        name: str,
        *,
        case_sensitive: bool = False,
        allow_args: bool = True,
    ):
        self.prefix = prefix
        self.name = name
        self.case_sensitive = case_sensitive
        self.allow_args = allow_args

    def __call__(self, message: Message) -> bool:
        if not message.text:
            return False

        text = message.text if self.case_sensitive else message.text.lower()
        prefix = self.prefix if self.case_sensitive else self.prefix.lower()
        name = self.name if self.case_sensitive else self.name.lower()

        if not text.startswith(prefix + name):
            return False

        if self.allow_args:
            rest = text[len(prefix) + len(name):]
            return rest == "" or rest.startswith(" ")

        return text == prefix + name


class Handler(BaseModel):
    name: str
    description: str
    handler: Callable[..., Awaitable[None]]
    filters: list = []
    model_config = ConfigDict(arbitrary_types_allowed=True)


class Processor:
    def __init__(self):
        self.commands: list[Handler] = []

    def add(self, *filters: Filter):
        def decorator(func):
            self.commands.append(Handler(
                name=func.__name__,
                description=func.__doc__ or "",
                handler=func,
                filters=list(filters),
            ))
            return func
        return decorator

    async def process(self, message: Message):
        for command in self.commands:
            if all(f(message) for f in command.filters):
                await command.handler(message)
                return  # первая совпавшая команда выигрывает

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

    async def long_poll_async(self, processor: Processor):
        resp = await self._call_api("messages.getLongPollServer")
        resp = resp.get("response", {})
        ts = resp.get("ts")
        key = resp.get("key")

        params = {"wait": 25, "key": key, "version": 3, "act": "a_check", "ts": ts, "mode": 2}
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    response = await client.get(URL, params=params, timeout=30)
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
        return await self._call_api("messages.send", params=params)

    async def get_user_info(self, user_id: int):
        params = {"user_ids": user_id}
        return await self._call_api("users.get", params=params)


api = OvkApi(
    ### creds or token
    ) 
         
processor = Processor()


@processor.add(Command(prefix=".", name="привет"))
async def hello_command(message: Message):
    """Приветствие пользователя"""
    await api.send_message(peer_id=message.peer_id, message="Привет! Как дела?")


@processor.add(Text("хай"))
async def hi_command(message: Message):
    """Реакция на точное 'хай'"""
    await api.send_message(peer_id=message.peer_id, message="Хай!")


@processor.add(Command(prefix="/", name="ping"), Command(prefix="/", name="pong"))
async def ping_command(message: Message):
    """Реагирует и на /ping, и на /pong"""
    await api.send_message(peer_id=message.peer_id, message="pong")


asyncio.run(api.long_poll_async(processor))

## photo13513_80 щперма
