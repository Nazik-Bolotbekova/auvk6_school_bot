from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboard import  inline_keyboard_2
from middleware import ModeratorMiddleware
from states import  AllStates
from utils.service import choose_topic, analyze_message
from utils.bot_logconfig import logger
from config import BOT_TOKEN, GROUP_ID, FILTER_GROUP_ID
from handlers.message_handlers import db



bot = Bot(token=BOT_TOKEN)
router = Router()

router.message.middleware(ModeratorMiddleware(bot,FILTER_GROUP_ID,db))



@router.message(AllStates.request)
async def save_request(message: Message, state: FSMContext):
    await state.update_data(request=message.text)
    await state.set_state(AllStates.anon_not_anon)
    await message.answer('Окей, теперь выбери способ отправки:', reply_markup=inline_keyboard_2)
    logger.info(f'ANON_NOT_ANON CHOICE GIVEN TO {message.from_user.username}')


@router.message(AllStates.problem)
async def save_problem(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)
    await state.set_state(AllStates.anon_not_anon)
    await message.answer("Окей, теперь выбери способ отправки 🖇", reply_markup=inline_keyboard_2)
    logger.info(f'ANON_NOT_ANON CHOICE GIVEN TO {message.from_user.username}')




@router.callback_query(F.data.in_(['anon', 'not_anon']))
async def anon_not_anon(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_type = data.get('type')
    text = data.get(message_type)
    topic_id = choose_topic(message_type)

    if not text:
        await callback.message.answer('Ошибка: текст не найден\n\n'
                                      'Попробуй начать заново /start')
        logger.info(f'NOT FOUND {message_type} in {callback.message.chat.id} by {callback.message.from_user.username}')
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
            logger.info(f'SAVED {callback.message.from_user.username} message to db STATUS ANON')
        except Exception as e:
            logger.error(f'FAILED to save ANON message {callback.message.from_user.username} to db {e}')
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
        logger.info(f'NOT_FOUND {message_type} in {message.chat.id} by {message.from_user.username}')
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
            logger.info(f'SAVED {message.from_user.username} message to db STATUS NOT_ANON')
        except Exception as e:
            logger.error(f'FAILED to SAVE {data.get("full_name_and_grade")}: {text} message: {e}')
            return
        await state.update_data({message_type: None})
        await message.answer('Сообщение отправлено! ✅')
        await state.clear()




@router.callback_query(F.data.in_(['request','problem']))
async def callback_query(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'request':
        await state.set_state(AllStates.request)
        await state.update_data(type='request')
        await callback.message.answer('Напиши свою идею ✏')
        logger.info('REQUEST TEXT SENT')

    elif callback.data == 'problem':
        await state.set_state(AllStates.problem)
        await state.update_data(type='problem')
        await callback.message.answer('Опиши проблему, которую заметил(а) в школе 🏫')
        logger.info('PROBLEM TEXT SENT')

