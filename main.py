import asyncio
import os

from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F


from handlers import router


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)









# @dp.message(AllStates.anon_not_anon)
# async def anon_not_anon(message: Message, state: FSMContext):
#     await state.update_data(anon_not_anon=message.text)
#     data = await state.get_data()
#
#     if data['type'] == 'request':
#         text = data.get('request')
#     elif data['type'] == 'problem':
#         text = data.get('problem')
#
#
#     if data['anon_not_anon'].lower() in ('анонимно', 'анон'):
#         await bot.send_message(
#             chat_id=GROUP_ID,
#             text=(
#                 f"Сообщение: {text}"
#             ))
#
#         await message.answer('Ваше сообщение принято!')
#
#     elif data['anon_not_anon'].lower() in ('не анонимно', 'не анон','неанон'):
#         await bot.send_message(
#             chat_id=GROUP_ID,
#             text=(
#                 f"Сообщение от {message.from_user.username}: {text}"
#             ))
#
#
#         await message.answer('Ваше сообщение принято!')
#
#     else:
#
#
#         await message.answer('Напишите правильно: анонимно - анон, не анонимно - не анон')
#
#
#
#
#
#
#
#
# @dp.message(AllStates.problem)
# async def save_message(message: Message, state: FSMContext):
#     await state.update_data(problem=message.text)
#     await state.set_state(AllStates.anon_not_anon)
#     await message.answer('Анонимно или не анонимно?')
#













async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())






