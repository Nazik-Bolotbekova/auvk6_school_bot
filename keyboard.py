from aiogram import types

inline_keyboards = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Оставить предложение 📝", callback_data="request"),
        ],
        [
            types.InlineKeyboardButton(text="Сообщить о проблеме ⚠️", callback_data="problem")
        ]
    ],
    resize_keyboard=True
)