from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main_page_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="Оставить предложение📝")
        ],
        [
            types.KeyboardButton(text="Сообщить о проблеме ⚠")
        ]
    ],
    resize_keyboard=True
)