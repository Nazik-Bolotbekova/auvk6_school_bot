import asyncio
import os

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, CallbackQuery

from keyboard import inline_keyboards
from states import  AllStates

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()



@dp.message(Command('start'))
async def start_command(message: Message):
    photo = FSInputFile("image/photo_5467860983105060122_y.jpg")        # старт команда
    text = ("<b>Привет!</b> Я твой школьный бот.\n"
            "Можно писать <i>анонимно</i> или от своего имени")
    await message.answer_photo(photo=photo, caption=text,parse_mode=ParseMode.HTML, reply_markup=inline_keyboards)


@dp.callback_query()
async def callback_query(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'request':
        await state.set_state(AllStates.request)
        await state.update_data(type='request')
        await callback.message.answer('Напиши свою идею ✏')             # коллбэки на инлайн клавиатуру и фсм
    elif callback.data == 'problem':
        await state.set_state(AllStates.problem)
        await state.update_data(type='problem')
        await callback.message.answer('Опиши проблему, которую заметил(а) в школе 🏫')
    else:
        pass


@dp.message(AllStates.request)
async def save_message(message: Message, state: FSMContext):
    await state.update_data(request=message.text)
    await state.set_state(AllStates.anon_not_anon)
    await message.answer('Анонимно или не анонимно?')



@dp.message(AllStates.problem)
async def save_message(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)
    await state.set_state(AllStates.anon_not_anon)
    await message.answer('Анонимно или не анонимно?')



@dp.message(AllStates.anon_not_anon)
async def anon_not_anon(message: Message, state: FSMContext):
    await state.update_data(anon_not_anon=message.text)
    data = await state.get_data()

    if data['type'] == 'request':
        text = data.get('request')
    elif data['type'] == 'problem':
        text = data.get('problem')


    if data['anon_not_anon'].lower() in ('анонимно', 'анон'):
        await bot.send_message(
            chat_id=GROUP_ID,
            text=(
                f"Сообщение: {text}"
            ))

        await message.answer('Ваше сообщение принято!')

    elif data['anon_not_anon'].lower() in ('не анонимно', 'не анон','неанон'):
        await bot.send_message(
            chat_id=GROUP_ID,
            text=(
                f"Сообщение от {message.from_user.username}: {text}"
            ))


        await message.answer('Ваше сообщение принято!')

    else:
        await message.answer('Напишите правильно: анонимно - анон, не анонимно - не анон')























async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())






