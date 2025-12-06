import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from handlers.message_handlers import router as message_router
from handlers.callback_handlers import router as callback_router
from handlers.message_handlers import db



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(message_router)
dp.include_router(callback_router)



async def main():
    await db.init_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

