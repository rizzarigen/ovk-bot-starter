from core import OvkApi, Processor
from core.filters import Command, Text
from core.types import Message, Photo
import asyncio
import dotenv
import os

dotenv.load_dotenv()


processor = Processor()

@processor.add(Command(prefix = ".", name="ди"))
async def di_command(message: Message, di_stuff: str):
    await message.reply(di_stuff)

@processor.add(Command(prefix='.', name="ответ"))
async def otvet_command(message: Message):
    await message.answer("опааа")
    
@processor.add(Command(prefix='.', name="фото"))
async def otvet_command(message: Message):
    photo = Photo(path='photos/test.jpg')
    await message.answer("опааа", photo=photo)
    
@processor.add(Command(prefix='.', name="реплай"))
async def otvet_command(message: Message):
    await message.reply(".реплай" )
    
### tail = None is important if you gonna use it. Temporarily workarounded, yep.
@processor.add(Command(prefix='.', name="арги", req_args=["arg1", "arg2"]))
async def iskl_command(message: Message, arg1, arg2, tail = None):
    await message.answer(f"Опа! Аргументы: {arg1=}, {arg2=}, {tail=}")
    
 
    
    


async def main():
    
    api = OvkApi.by_credentials(
        login=os.getenv("LOGIN"),
        password=os.getenv("PASSWORD")
    )
    
    ### or OvkApi.by_token(token)
    

    some_stuff_to_test_di = "DI работает!"
    await processor.add_di("di_stuff", some_stuff_to_test_di)

    
    await api.start_polling(processor)

       
try:
    print("Start polling...")
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nShutting down...")
