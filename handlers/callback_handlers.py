from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboard import  inline_keyboard_2, inline_keyboard_3
from states import  AllStates
from utils.service import choose_topic, analyze_message
from utils.bot_logconfig import logger
from config import BOT_TOKEN, GROUP_ID, FILTER_GROUP_ID
from handlers.message_handlers import db
from aiogram.filters import StateFilter

bot = Bot(token=BOT_TOKEN)
router = Router()



async def handle_toxic_message(message: Message):
    user_id = message.from_user.id

    warnings = await db.get_warnings(user_id)
    warnings += 1
    await db.update_warnings(user_id, warnings)

    await bot.send_message(FILTER_GROUP_ID, f"{message.from_user.username}: {message.text}")

    if warnings == 1:
        await message.answer('Без токсичности! Это твое первое предупреждение.')
        logger.info(f'FIRST WARNING {message.from_user.username}: {message.text}')
    elif warnings == 2:
        await message.answer('Пиши по делу! Это твое второе предупреждение')
        logger.info(f'SECOND WARNING {message.from_user.username}: {message.text}')
    elif warnings >= 3:
        await message.answer('Данные о твоем аккаунте улетели в чат модерации. Я предупреждал')
        logger.info(f'THIRD WARNING {message.from_user.username}: {message.text}')
    return



@router.message(F.chat.type == 'private',)
async def moderator_entry(message: Message, state: FSMContext):
    current_state = await state.get_state()
    logger.info(f"MODERATOR CHECK: state={current_state}, text={message.text[:50]}")


    analysis = await analyze_message(message_text=message.text)
    logger.info(f"ANALYSIS RESULT: {analysis}")

    if analysis == "not_okay":
        await handle_toxic_message(message)
        return

    elif analysis == "model_failed":
        await message.answer('Фильтр бота сейчас завис, попробуй еще раз')
        logger.info(f"MODEL FAILED for {message.from_user.username}")

    logger.info(f"MESSAGE PASSED FILTER, going to next handlers: {message.text[:50]}")








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
    current_state = await state.get_state()

    if current_state in ['AllStates:request', 'AllStates:problem']:
        await callback.message.answer('Хочешь вернуться? ↩', reply_markup=inline_keyboard_3)
        return


    if callback.data == 'request':
        await state.set_state(AllStates.request)
        await state.update_data(type='request')
        await callback.message.answer('Напиши свою идею ✏')
        logger.info('request text sent')
                                                                  # коллбэки на инлайн клавиатуру и фсм
    elif callback.data == 'problem':
        await state.set_state(AllStates.problem)
        await state.update_data(type='problem')
        await callback.message.answer('Опиши проблему, которую заметил(а) в школе 🏫')
        logger.info('problem text sent')



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
            logger.info(f"CANCEL confirmed by {callback.from_user.username}")
        elif callback.data == 'no_cancel':
            current_state = await state.get_state()
            await state.set_state(current_state)
            await callback.message.answer('Продолжай писать свое сообщение')
            logger.info(f"CANCEL rejected by {callback.from_user.username}")



@router.message(AllStates.problem)
async def save_problem(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)
    await state.set_state(AllStates.anon_not_anon)
    await message.answer("Окей, теперь выбери способ отправки 🖇", reply_markup=inline_keyboard_2)



# @router.message(F.chat.type == 'private')
# async def moderator_entry(message: Message):
#     analysis = await analyze_message(message_text=message.text)
#
#     if analysis == "not_okay":
#         await handle_toxic_message(message)
#         return
#
#     elif analysis == "model_failed":
#         await message.answer('Фильтр бота сейчас завис, попробуй еще раз')
#         logger.info(f"MODEL FAILED for {message.from_user.username}")
#         return False
#
#     return False



