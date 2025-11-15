import asyncio
import os

from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from handlers import router, db


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(router)










async def main():
    await db.init_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())






