from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.filters import  Command
from aiogram.types import Message, FSInputFile, CallbackQuery
from keyboard import inline_keyboards, inline_keyboard_2, inline_keyboard_3
from states import  AllStates
from database.db_interaction import Database
from utils.service import chunk_text, log_location_chat, choose_topic, generate_summary
from datetime import datetime, timezone, timedelta
from utils.bot_logconfig import logger
from config import BOT_TOKEN, GROUP_ID


db = Database()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


@router.message(Command('start'))
async def start_command(message: Message):
    logger.info(f"User #{message.from_user.id}/{message.from_user.username} started the bot.")
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
    )
    logger.info(f'Saved User #{message.from_user.id}/{message.from_user.username} to db')
    photo = FSInputFile("image/photo_5467860983105060122_y.jpg")        # старт команда
    text = ("<b>Привет!</b> Я твой школьный бот.\n"
            "Можно писать <i>анонимно</i> или от своего имени.\n\n\n<b>Если хочешь начать заново или написать что-то новое, просто нажми /start или введи эту команду.</b>")
    await message.answer_photo(photo=photo, caption=text,parse_mode=ParseMode.HTML, reply_markup=inline_keyboards)
    logger.info(f'Sent start screen to user {message.from_user.id}/{message.from_user.username}')



@router.message(Command('stats'))
async def stats_command(message: Message):
    stats = await db.get_stats()                # команда статов
    text = (f"Всего сообщений: {stats['total_messages']}\n"
            f"Всего анонимных сообщений: {stats['anon_messages']}\n"
            f"Всего пользователей: {stats['total_users']}")
    await message.answer(text)
    if message.chat.type == 'private':
        logger.info(f'User #{message.from_user.id}/{message.from_user.username} requested stats in a PRIVATE chat')
    else:
        logger.info(f'User #{message.from_user.id}/{message.from_user.username} requested stats in a CHAT #{message.chat.id}')



@router.message(Command('get_messages'))
async def get_all_messages(message: Message):      # команда списка всех смс из бд
    messages = await db.get_all_messages()
    if not messages:
        await message.answer("Пока сообщений нет")
        return
    text = ""
    for msg in messages:
        utc = datetime.fromisoformat(msg['created_at']).replace(tzinfo=timezone.utc)
        local = utc.astimezone(timezone(timedelta(hours=6)))
        formatted = local.strftime("%d.%m.%Y %H:%M")
        text += (
            f"📨Сообщение #{msg['id']}\n"
            f"От: @{msg['username']}\n"
            f"Текст: {msg['message']}\n"
            f"Аноним: {msg['is_anon']}\n"
            f"Время: {formatted}\n\n"
        )
    for chunk in chunk_text(text):
        await message.answer(chunk)
        log_location_chat(message, 'requested get_messages command')



@router.message(Command('get_users'))
async def get_all_users(message: Message):
    users = await db.get_users()                 # команда списка всех юзеров из бд
    if not users:
        await message.answer('Пользователей пока нет')
        return
    text = ""
    for user in users:
        text += (
            f"Список пользователей:\n "
            f"#{user['user_id']} - {user['username']}\n\n"
        )
    for chunk in chunk_text(text):
        await message.answer(chunk)
        log_location_chat(message, 'requested get_users command')



@router.message(Command('help'))
async def help_command(message: Message):
    text = (f"Привет! Команды которыми ты можешь воспользоваться:\n\n"      # инструкция
            f"/get_messages - список всех сообщений\n"
            f"/get_users - список всех пользователей\n"
            f"/stats - статы\n"
            f"/help - данная инструкция")
    await message.answer(text)
    log_location_chat(message, 'requested /help command')



@router.callback_query(F.data.in_(['anon', 'not_anon']))
async def anon_not_anon(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_type = data.get('type')
    text = data.get(message_type)
    topic_id = choose_topic(message_type)

    if not text:
        await callback.message.answer('Ошибка: текст не найден\n\n'
                                      'Попробуй начать заново /start')
        logger.info(f'Not found {message_type} in {callback.message.chat.id} by {callback.message.from_user.username}')
        return
    if callback.data == 'anon':
        try:
            await bot.send_message(GROUP_ID, f"Анонимное сообщение: {text}",message_thread_id=topic_id)
        except Exception as e:
            logger.error(f'FAILED to send ANON message to {callback.message.chat.id}: {e}')
            await callback.message.answer('Не получилость отправить сообщение. повтори попытку позже')
            return

        try:
            await db.add_message(
                user_id=callback.from_user.id,
                username=callback.from_user.username,
                message=text,
                is_anon=True
            )
            logger.info(f'Saved user`s-{callback.message.from_user.username}/message-({text}) to db STATUS ANON')
        except Exception as e:
            logger.error(f'FAILED to save ANON message ({callback.message.from_user.username}-{text}) to db {e}')
            await callback.message.answer('Не удалось сохранить сообщение. повтори попытку позже')
            return
        await state.update_data({message_type: None})
        await callback.message.answer('Сообщение отправлено! ✅')
    elif callback.data == 'not_anon':
        await state.set_state(AllStates.full_name_and_grade)
        await callback.message.answer('Напиши имя, фамилию и класс 📝:')


@router.message(AllStates.full_name_and_grade)
async def full_name_and_grade(message: Message, state: FSMContext):
    await state.update_data(full_name_and_grade=message.text)
    data = await state.get_data()
    message_type = data.get('type')
    text = data.get(message_type)
    topic_id = choose_topic(message_type)
    if not text:
        await message.answer('Ошибка: текст не найден\n\n'
                                      'Попробуй начать заново /start')
        logger.info(f'Not found {message_type} in {message.chat.id} by {message.from_user.username}')
        return
    if data['type'] == 'request' or data['type'] == 'problem':
        try:
            await bot.send_message(GROUP_ID, f'Сообщение от ученика {data.get("full_name_and_grade")}: {text}', message_thread_id=topic_id)
        except Exception as e:
            logger.error(f'FAILED to SEND {data.get("full_name_and_grade")}: {text} message: {e}')
            return
        try:
            await db.add_message(
                user_id=message.from_user.id,
                username=message.from_user.username,
                message=text,
                is_anon=False
            )
            logger.info(f'Saved user`s {message.from_user.username}/message ({text}) to db STATUS NOT_ANON')
        except Exception as e:
            logger.error(f'FAILED to SAVE {data.get("full_name_and_grade")}: {text} message: {e}')
            return
        await state.update_data({message_type: None})
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
async def save_request(message: Message, state: FSMContext):
    await state.update_data(request=message.text)
    await state.set_state(AllStates.anon_not_anon)
    await message.answer('Окей, теперь выбери способ отправки:', reply_markup=inline_keyboard_2)



@router.callback_query(F.data.in_(['yes_cancel', 'no_cancel']))
async def cancel_message(callback: CallbackQuery, state: FSMContext):         # хэндлер коллбэков отмены
        if callback.data == 'yes_cancel':
            await state.clear()
            await callback.message.answer('Действие отменено\n\nЧтобы начать заново, нажми /start')
            logger.info(f'User {callback.from_user.username} called CANCEL command')
        elif callback.data == 'no_cancel':
            current_state = await state.get_state()
            await state.set_state(current_state)
            await callback.message.answer('Продолжай писать свое сообщение')
            logger.info(f'User {callback.from_user.username} called NO CANCEL command')



@router.message(AllStates.problem)
async def save_problem(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)
    await state.set_state(AllStates.anon_not_anon)
    await message.answer("Окей, теперь выбери способ отправки 🖇", reply_markup=inline_keyboard_2)
    logger.info('')


@router.message(Command('generate_report'))
async def generate_report(message: Message):
    user_messages = await db.get_all_messages()
    report = await generate_summary(user_messages)
    await message.answer(report)
