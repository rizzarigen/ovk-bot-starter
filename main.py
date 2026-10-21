from core import OvkApi, Processor
from core.filters import Command, Text
from core.types import Message, Photo
import asyncio
import dotenv
import os

dotenv.load_dotenv()


processor = Processor()


#################################################
#               DEPRECATED METHODS              #
#################################################


#@processor.add(Command(prefix=".", name="привет"))
#async def hello_command(message: Message, api: OvkApi):
#    """Приветствие пользователя"""
#    await api.send_message(peer_id=message.peer_id, message="Привет! Как дела?")
#    ### deprecated


#@processor.add(Text("хай"))
#async def hi_command(message: Message, api: OvkApi):
#    """Реакция на точное 'хай'"""
#    await api.send_message(peer_id=message.peer_id, message="Хай!")
#    ### deprecated


#@processor.add(Command(prefix=".", name="пинг"))
#async def ping_command(message: Message, api: OvkApi):
#    """Реагирует и на /ping, и на /pong"""
#    print(message.text)
#    await api.send_message(peer_id=message.peer_id, message="pong")
#    ### deprecated
    
#@processor.add(Command(prefix=".", name="пикча"))
#async def pikcha_command(message: Message, api: OvkApi):
#    await api.send_photo(peer_id=message.peer_id, photo_path="photos/test.jpg", message="Вот твоя пикча!")
#    ### deprecated

#@processor.add(Command(prefix=".", name="пикча2"))
#async def pikcha_command(message: Message, api: OvkApi):
#    photo = Photo(path='photos/test.jpg')
#    await api.send_message(peer_id=message.peer_id, message="Держи!", photo=photo)
#    ### deprecated
    
    
    
#################################################
#               ACTUAL METHODS                  #
#################################################

@processor.add(Command(prefix='.', name="ответ"))
async def otvet_command(message: Message):
    await message.answer("опааа")
    
@processor.add(Command(prefix='.', name="фото"))
async def otvet_command(message: Message):
    photo = Photo(path='photos/test.jpg')
    await message.answer("опааа", photo=photo)
    
@processor.add(Command(prefix='.', name="реплай"))
async def otvet_command(message: Message):
    print(message.text)
    await message.reply("+реп" )
    

@processor.add(Command(prefix='.', name="арги", req_args=["arg1", "arg2"]))
async def iskl_command(message: Message, arg1, arg2):
    tail = message.args_rest
    await message.answer(f"Опа! Аргументы: {arg1=}, {arg2=}, {tail=}")
    
 
    
    


async def main():
    
    ### FROM NOW WE USE BRAND NEW FACTORY FUNCTIONS TO INSTANTIATE OVKAPI OBJECT!
    
    api = OvkApi.by_credentials(
        login=os.getenv("LOGIN"),
        password=os.getenv("PASSWORD")
    )
    
    ### or OvkApi.by_token(token)
    
    
    
    
    
    ### await processor.add_di("api", api) 
    ### no need to DI the API instance if you gonna use actual methods
    
    await api.long_poll_async(processor)
       

asyncio.run(main())
