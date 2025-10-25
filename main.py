import asyncio
import os

from aiogram.enums import ParseMode
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from keyboard import inline_keyboards

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart)
async def start_command(message: Message):
    photo = FSInputFile("image/photo_5467860983105060122_y.jpg")
    text = ("<b>Привет!</b> Я твой школьный бот.\n"
            "Можно писать <i>анонимно</i> или от своего имени")
    await message.answer_photo(photo=photo, caption=text,parse_mode=ParseMode.HTML, reply_markup=inline_keyboards)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())






