import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from handlers import router, db




bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)



async def main():
    await db.init_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())






