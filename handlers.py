import os
from aiogram import Bot, Dispatcher, Router, F

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv

from aiogram.filters import  Command
from aiogram.types import Message, FSInputFile, CallbackQuery

from keyboard import inline_keyboards, inline_keyboard_2, inline_keyboard_3
from states import  AllStates
from db_interaction import Database

from additional_functions import chunk_text

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')

db = Database()


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

router = Router()



@router.message(Command('start'))
async def start_command(message: Message):
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
    )
    photo = FSInputFile("image/photo_5467860983105060122_y.jpg")        # старт команда
    text = ("<b>Привет!</b> Я твой школьный бот.\n"
            "Можно писать <i>анонимно</i> или от своего имени.\n\n\n<b>Если хочешь начать заново или написать что-то новое, просто нажми /start или введи эту команду.</b>")
    await message.answer_photo(photo=photo, caption=text,parse_mode=ParseMode.HTML, reply_markup=inline_keyboards)




@router.message(Command('stats'))
async def stats_command(message: Message):
    stats = await db.get_stats()
    text = (f"Всего сообщений: {stats['total_messages']}\n"
            f"Всего анонимных сообщений: {stats['anon_messages']}\n"
            f"Всего пользователей: {stats['total_users']}")
    await message.answer(text)


@router.message(Command('get_messages'))
async def get_all_messages(message: Message):
    messages = await db.get_all_messages()  # <-- это список

    if not messages:
        await message.answer("Пока сообщений нет 🙂")
        return

    text = ""

    for msg in messages:
        text += (
            f"📨Сообщение #{msg['id']}\n"
            f"От: @{msg['username']}\n"
            f"Текст: {msg['message']}\n"
            f"Аноним: {msg['is_anon']}\n\n"
        )

    for chunk in chunk_text(text):
        await message.answer(chunk)










@router.callback_query(F.data.in_(['anon', 'not_anon']))
async def anon_not_anon(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_type = data.get('type')  # безопасно
    text = data.get(message_type, 'Ошибка: текст не найден')

    if callback.data == 'anon':
        await bot.send_message(GROUP_ID, f"Анонимное сообщение: {text}")
        await db.add_message(
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            message=text,
            is_anon=True
        )
        await callback.message.answer('Сообщение отправлено! ✅')

    elif callback.data == 'not_anon':
        await state.set_state(AllStates.full_name_and_grade)
        await callback.message.answer('Напиши имя, фамилию и класс 📝:')



@router.message(AllStates.full_name_and_grade)
async def full_name_and_grade(message: Message, state: FSMContext):
    await state.update_data(full_name_and_grade=message.text)
    data = await state.get_data()
    msg_type = data.get('type')
    text = data.get(msg_type, 'Ошибка: текст не найден')

    if data['type'] == 'request' or data['type'] == 'problem':
        await bot.send_message(GROUP_ID, f'Сообщение от ученика {data.get("full_name_and_grade")}: {text}')
        await db.add_message(
            user_id=message.from_user.id,
            username=message.from_user.username,
            message=text,
            is_anon=False
        )
        await message.answer('Сообщение отправлено! ✅')
    await state.clear()





@router.callback_query(F.data.in_(['request','problem']))
async def callback_query(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state in ['AllStates:request', 'AllStates:problem']:
        await callback.message.answer('Хочешь вернуться? ↩', reply_markup=inline_keyboard_3)
        return


    if callback.data == 'request':
        await state.set_state(AllStates.request)
        await state.update_data(type='request')
        await callback.message.answer('Напиши свою идею ✏')
                                                                  # коллбэки на инлайн клавиатуру и фсм
    elif callback.data == 'problem':
        await state.set_state(AllStates.problem)
        await state.update_data(type='problem')
        await callback.message.answer('Опиши проблему, которую заметил(а) в школе 🏫')





@router.message(AllStates.request)
async def save_message(message: Message, state: FSMContext):
    await state.update_data(request=message.text)
    await state.set_state(AllStates.anon_not_anon)
    await message.answer('Окей, теперь выбери способ отправки:', reply_markup=inline_keyboard_2)




@router.callback_query(F.data.in_(['yes_cancel', 'no_cancel']))
async def cancel_message(callback: CallbackQuery, state: FSMContext):

        if callback.data == 'yes_cancel':
            await state.clear()
            await callback.message.answer('Действие отменено\n\nЧтобы начать заново, нажми /start')
        elif callback.data == 'no_cancel':
            current_state = await state.get_state()
            await state.set_state(current_state)
            await callback.message.answer('Продолжай писать свое сообщение')













@router.message(AllStates.problem)
async def save_message(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)
    await state.set_state(AllStates.anon_not_anon)
    await message.answer("Окей, теперь выбери способ отправки 🖇", reply_markup=inline_keyboard_2)





