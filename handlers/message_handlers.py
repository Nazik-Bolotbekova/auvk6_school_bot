from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import  Command
from aiogram.types import Message, FSInputFile
from keyboard import inline_keyboards
from database.db_interaction import Database
from utils.service import chunk_text, log_location_chat, generate_summary
from datetime import datetime, timezone, timedelta
from utils.bot_logconfig import logger


db = Database()
router = Router()


@router.message(Command('start'))
async def start_command(message: Message):
    logger.info(f"START by {message.from_user.username} in {message.chat.id} ")
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
    )
    logger.info(f'SAVED user #{message.from_user.id}/{message.from_user.username} to db')
    photo = FSInputFile("image/photo_5467860983105060122_y.jpg")        # старт команда
    text = ("<b>Привет!</b> Я твой школьный бот.\n"
            "Можно писать <i>анонимно</i> или от своего имени.\n\n\n<b>Если хочешь начать заново или написать что-то новое, просто нажми /start или введи эту команду.</b>")
    await message.answer_photo(photo=photo, caption=text,parse_mode=ParseMode.HTML, reply_markup=inline_keyboards)
    logger.info(f'START screen sent to {message.from_user.username}')



@router.message(Command('stats_5'))
async def stats_command(message: Message):
    stats = await db.get_stats()                # команда статов
    text = (f"Всего сообщений: {stats['total_messages']}\n"
            f"Всего анонимных сообщений: {stats['anon_messages']}\n"
            f"Всего пользователей: {stats['total_users']}")
    await message.answer(text)
    if message.chat.type == 'private':
        logger.info(f'STATS requested by {message.from_user.id} in a PRIVATE chat')
    else:
        logger.info(f'STATS requested by {message.from_user.id} in a CHAT #{message.chat.id}')



@router.message(Command('get_messages_5'))
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
        log_location_chat(message, 'GET_MESSAGES REQUESTED')

@router.message(Command('get_last_messages_10'))
async def get_last_messages(message: Message):
    messages = await db.get_last_messages()
    if not messages:
        await message.answer('Пока сообщений нет')
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
            log_location_chat(message, 'GET_LAST_MESSAGES REQUESTED')


@router.message(Command('get_users_5'))
async def get_all_users(message: Message):
    users = await db.get_users()                 # команда списка всех юзеров из бд
    if not users:
        await message.answer('Пользователей пока нет')
        return
    text = "Список пользователей:\n"
    for user in users:
        text += (
            f"#{user['user_id']} - {user['username']}\n\n"
        )
    for chunk in chunk_text(text):
        await message.answer(chunk)
        log_location_chat(message, 'GET_USERS sent')



@router.message(Command('help_5'))
async def help_command(message: Message):
    text = (f"Привет! Команды которыми ты можешь воспользоваться:\n\n"      # инструкция
            f"/get_messages_5 - список всех сообщений\n"
            f"/get_last_messages_10 - cписок последних десяти сообщений\n"
            f"/get_users_5 - список всех пользователей\n"
            f"/stats_5 - статы\n"
            f"/generate_report_5 - генерация отчета исходя из всех сообщений\n"
            f"/help_5 - данная инструкция")
    await message.answer(text)
    log_location_chat(message, 'HELP/ requested by')



@router.message(Command('generate_report_5'))
async def generate_report(message: Message):
    user_messages = await db.get_all_messages()
    report = await generate_summary(user_messages)
    await message.answer(report)
    log_location_chat(message, 'REPORT generated by')


@router.message(Command('id_'))
async def id_(message: Message):
    id_2 = str(message.chat.id)
    await message.answer(id_2)

