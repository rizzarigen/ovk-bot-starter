

import asyncio
from core import Bot, Message

TOKEN = "(агащас)"


bot = Bot(token=TOKEN, instance_url="https://api.openvk.org")

# Реакция на команду /start или /help
@bot.message_handler("/start", "/help")
async def start_cmd(message: Message):
    await message.answer("Привет! Я бот для OpenVK, написанный на асинхронном Python 🚀")


# Реакция на точный текст
@bot.message_handler(text="пинг")
async def ping_cmd(message: Message):
    await message.answer("ПОНГ! 🏓")




if __name__ == "__main__":
    asyncio.run(bot.api.call("messages.send", group_id=12023, message="йоу"))
    asyncio.run(bot.start_polling())

## photo13513_80 щперма