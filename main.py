from core import OvkApi, Processor
from core.filters import Command, Text
from core.types import Message
import asyncio

processor = Processor()


@processor.add(Command(prefix=".", name="привет"))
async def hello_command(message: Message, api: OvkApi):
    """Приветствие пользователя"""
    await api.send_message(peer_id=message.peer_id, message="Привет! Как дела?")


@processor.add(Text("хай"))
async def hi_command(message: Message, api: OvkApi):
    """Реакция на точное 'хай'"""
    await api.send_message(peer_id=message.peer_id, message="Хай!")


@processor.add(Command(prefix=".", name="пинг"))
async def ping_command(message: Message, api: OvkApi):
    """Реагирует и на /ping, и на /pong"""
    print(message.text)
    await api.send_message(peer_id=message.peer_id, message="pong")

async def main():
    
    api = OvkApi(
        login="",
        password="" ## or token= instead of credentials
    ) 
    
    await processor.add_di("api", api)
    
    await api.long_poll_async(processor)
       

asyncio.run(main())
