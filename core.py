import asyncio
import logging
from typing import Callable, List, Optional
import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("OpenVKBot")


class Message:
    def __init__(self, data: dict, api: "OpenVKAPI"):
        self.raw = data
        self.api = api
        self.id: int = data.get("id", 0)
        self.user_id: int = data.get("user_id") or data.get("from_id", 0)
        self.text: str = data.get("body") or data.get("text", "")
        self.peer_id: int = data.get("peer_id", self.user_id)

    async def answer(self, text: str) -> dict:
        return await self.api.messages_send(peer_id=self.peer_id, message=text)


class OpenVKAPI:
    def __init__(self, token: str, instance_url: str = "https://openvk.su"):
        self.token = token
        self.instance_url = instance_url.rstrip("/")
        self.api_url = f"{self.instance_url}/method"

    async def call(self, method: str, **params) -> dict:
        params["access_token"] = self.token
        params["v"] = params.get("v", "5.131")

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            logger.debug(f"Отправка API запроса к {method}...")
            async with session.get(f"{self.api_url}/{method}", params=params) as resp:
                data = await resp.json()
                if "error" in data:
                    logger.error(f"API Error [{method}]: {data['error']}")
                return data.get("response", data)

    async def messages_send(self, peer_id: int, message: str) -> dict:
        import random
        return await self.call(
            "messages.send",
            peer_id=peer_id,
            message=message,
            random_id=random.randint(1, 2147483647)
        )
        



class Router:
    def __init__(self):
        self.message_handlers: List[dict] = []

    def message_handler(self, *commands: str, text: Optional[str] = None):
        def decorator(func: Callable):
            self.message_handlers.append({
                "func": func,
                "commands": [c.lower() for c in commands],
                "text": text.lower() if text else None
            })
            return func
        return decorator

    async def process_message(self, message: Message):
        text_lower = message.text.lower().strip()
        first_word = text_lower.split()[0] if text_lower else ""

        for handler in self.message_handlers:
            if handler["commands"] and first_word in handler["commands"]:
                await handler["func"](message)
                return
            if handler["text"] and handler["text"] == text_lower:
                await handler["func"](message)
                return
            if not handler["commands"] and not handler["text"]:
                await handler["func"](message)
                return


class Bot:
    def __init__(self, token: str, instance_url: str = "https://openvk.su"):
        self.api = OpenVKAPI(token, instance_url)
        self.router = Router()

    def message_handler(self, *commands: str, text: Optional[str] = None):
        return self.router.message_handler(*commands, text=text)

    async def _get_longpoll_server(self) -> dict:
        logger.info("Запрашиваем LongPoll сервер у OpenVK...")
        return await self.api.call("messages.getLongPollServer", need_pts=0)

    async def start_polling(self):
        logger.info("Инициализация бота...")
        lp_data = await self._get_longpoll_server()

        if not isinstance(lp_data, dict):
            logger.error(f"Некорректный ответ API: {lp_data}")
            return

        server = lp_data.get("server")
        key = lp_data.get("key")
        ts = lp_data.get("ts")

        if not server or not key:
            logger.error(f"Не удалось получить LongPoll параметры. Ответ: {lp_data}")
            return

        logger.info("LongPoll сервер успешно получен. Начинаем прослушивание...")
# Нормализация адреса сервера
        if not server.startswith("http"):
            server = f"https://{server}"

        # Ставим таймаут чуть больше, чем параметр wait (35 сек)
        timeout = aiohttp.ClientTimeout(total=35)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            while True:
                try:
                    url = f"{server}?act=a_check&key={key}&ts={ts}&wait=25&mode=2&version=2"
                    logger.debug(f"Ожидание LongPoll ответа с ts={ts}...")
                    
                    async with session.get(url) as resp:
                        res = await resp.json()

                        if "failed" in res:
                            logger.warning(f"LongPoll вернул ошибку/сброс (failed={res.get('failed')}). Обновляем ключи...")
                            lp_data = await self._get_longpoll_server()
                            key, ts = lp_data.get("key"), lp_data.get("ts")
                            server = lp_data.get("server")
                            if not server.startswith("http"):
                                server = f"https://{server}"
                            continue

                        ts = res.get("ts", ts)
                        updates = res.get("updates", [])
                        for update in updates:
                            # Код 4 = Новое сообщение
                            if update[0] == 4:
                                flags = update[2]
                                # Если это не исходящее сообщение (флаг 2)
                                if not (flags & 2):
                                    msg_data = {
                                        "id": update[1],
                                        "flags": flags,
                                        "peer_id": update[3],
                                        "timestamp": update[4],
                                        "text": update[6],
                                        "from_id": update[7].get("from") if isinstance(update[6], dict) else update[3]
                                    }
                                    logger.info(f"Получено новое сообщение: '{msg_data['text']}' от {msg_data['peer_id']}")
                                    msg = Message(msg_data, self.api)
                                    asyncio.create_task(self.router.process_message(msg))

                except asyncio.TimeoutError:
                    logger.warning("Таймаут соединения с LongPoll. Повторный запрос...")
                except Exception as e:
                    logger.error(f"Ошибка в цикле LongPoll: {e}")
                    await asyncio.sleep(3)
