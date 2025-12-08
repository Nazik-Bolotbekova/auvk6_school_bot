import asyncio
import os
from aiohttp import web
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from utils.bot_logconfig import logger
from config import BOT_TOKEN
from handlers.message_handlers import router as message_router
from handlers.callback_handlers import router as callback_router
from handlers.message_handlers import db



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(message_router)
dp.include_router(callback_router)


async def health_check(request):
    """Endpoint для проверки, что бот живой"""
    return web.Response(text="Bot is running")


async def start_http_server():
    """Запускает HTTP сервер на порту для Render"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)

    runner = web.AppRunner(app)
    await runner.setup()

    # Render передает порт через переменную PORT
    port = int(os.getenv('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    print(f"HTTP сервер запущен на порту {port}")





async def main():
    await db.init_db()
    logger.info('DB initialized')
    await start_http_server()
    await asyncio.sleep(2)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

