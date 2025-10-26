import asyncio
import os

from aiogram.enums import ParseMode
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile, CallbackQuery

from keyboard import inline_keyboards, inline_keyboard_2


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(F.text)
async def message_handler(message: Message):
    await message.answer('Ваше сообщение принято!', reply_markup=inline_keyboard_2)
    await bot.send_message(
        chat_id=GROUP_ID,
        text=(
                 f"{message.text}"
             ))



@dp.message(CommandStart)
async def start_command(message: Message):
    photo = FSInputFile("image/photo_5467860983105060122_y.jpg")
    text = ("<b>Привет!</b> Я твой школьный бот.\n"
            "Можно писать <i>анонимно</i> или от своего имени")
    await message.answer_photo(photo=photo, caption=text,parse_mode=ParseMode.HTML, reply_markup=inline_keyboards)



@dp.callback_query()
async def callback_query(callback: CallbackQuery):
    if callback.data == 'request':
        await callback.message.answer('Напиши свою идею ✏')
    elif callback.data == 'problem':
        await callback.message.answer('Опиши проблему, которую заметил(а) в школе 🏫')
    else:
        pass



async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())






