import os
from aiogram import Bot, Dispatcher, Router, F

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv

from aiogram.filters import  Command
from aiogram.types import Message, FSInputFile, CallbackQuery

from keyboard import inline_keyboards, inline_keyboard_2
from states import  AllStates

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

router = Router()


@router.message(Command('start'))
async def start_command(message: Message):
    photo = FSInputFile("image/photo_5467860983105060122_y.jpg")        # старт команда
    text = ("<b>Привет!</b> Я твой школьный бот.\n"
            "Можно писать <i>анонимно</i> или от своего имени")
    await message.answer_photo(photo=photo, caption=text,parse_mode=ParseMode.HTML, reply_markup=inline_keyboards)



@router.callback_query(F.data.in_(['anon', 'not_anon']), AllStates.anon_not_anon)
async def anon_not_anon(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_type = data.get('type')  # безопасно
    text = data.get(msg_type, 'Ошибка: текст не найден')

    if callback.data == 'anon':
        await bot.send_message(GROUP_ID, f"Сообщение: {text}")
    else:
        await bot.send_message(GROUP_ID, f"Сообщение от {callback.from_user.username}: {text}")

    await callback.message.answer('Сообщение отправлено ✅!')
    await state.clear()









@router.callback_query()
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


@router.message(AllStates.request)
async def save_message(message: Message, state: FSMContext):
    await state.update_data(request=message.text)
    await state.set_state(AllStates.anon_not_anon)
    await message.answer('Cообщение принято, выберите способ отправки:', reply_markup=inline_keyboard_2)





