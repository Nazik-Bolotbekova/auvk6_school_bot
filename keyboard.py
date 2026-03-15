from aiogram import types

inline_keyboards = types.InlineKeyboardMarkup(        # клавиатура на message_type
    inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Оставить предложение 📝", callback_data="request")
        ],
        [
            types.InlineKeyboardButton(text="Сообщить о проблеме ⚠️", callback_data="problem")
        ]
    ],
    resize_keyboard=True
)


inline_keyboard_2 = types.InlineKeyboardMarkup(      # клавиатура на анонимность
    inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Анон 🕵️", callback_data="anon")
        ],
        [
            types.InlineKeyboardButton(text="Не анон 🙋", callback_data="not_anon")
        ]
    ],
)






