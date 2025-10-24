import asyncio
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart)
async def start_command(message: Message):
    photo = FSInputFile("image/photo_5467860983105060122_y.jpg")
    text = ("Привет! Я твой школьный бот где ты можешь...\n"
            "Можно писать как анонимно, так и от своего имени.")
    await message.answer_photo(photo=photo, caption=text)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())






