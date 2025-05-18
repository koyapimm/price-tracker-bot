import asyncio
from telegram import Bot

TOKEN = "7989116004:AAFFiYWlQHPOoihaD8PpVBKi_98Buu-utwI"

async def get_chat_id():
    bot = Bot(token=TOKEN)
    updates = await bot.get_updates()
    for u in updates:
        print("Chat ID:", u.message.chat.id)

asyncio.run(get_chat_id())
