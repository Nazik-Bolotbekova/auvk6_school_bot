from aiogram.types import Message
from bot_logconfig import logger


def chunk_text(text: str, size: int = 4096):
    return [text[i:i+size] for i in range(0, len(text), size)]

def log_location_chat(message: Message, action: str):
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    if message.chat.type == 'private':
        logger.info(f'User {user_id}/{username} {action} in PRIVATE chat')
    else:
        logger.info(f'User {user_id}/{username} {action} in CHAT {chat_id} chat')