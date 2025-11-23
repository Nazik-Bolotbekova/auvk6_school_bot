import httpx
from aiogram.types import Message
from utils.bot_logconfig import logger
from config import REQUEST_TOPIC_ID, PROBLEM_TOPIC_ID, OPEN_ROUTER_API


def chunk_text(text: str, size: int = 4096):
    return [text[i:i+size] for i in range(0, len(text), size)]  # чанкер для отправки # большого текста


def log_location_chat(message: Message, action: str):
    user_id = message.from_user.id
    username = message.from_user.username              # для логов (проверка чата либо лички)
    chat_id = message.chat.id
    if message.chat.type == 'private':
        logger.info(f'User {user_id}/{username} {action} in PRIVATE chat')
    else:
        logger.info(f'User {user_id}/{username} {action} in CHAT {chat_id} chat')


def choose_topic(message_type: str):
    if message_type == 'request':
        return REQUEST_TOPIC_ID
    elif message_type == 'problem':
        return PROBLEM_TOPIC_ID
    else:
        raise ValueError(f'Unknown message type: {message_type}')


async def generate_summary(messages):
    text_block = "\n".join(f"- {m['message']}" for m in messages)

    prompt = f"""

        Проанализируй список сообщений:
        
        {text_block}
                
        Сделай краткий отчёт:
        - какие темы чаще всего поднимают
        - какие проблемы повторяются
        - отчет не должен быть длинным но содержать все детали
        
        Формат отчёта:
        - Никакого Markdown.
        - Не используй символы *, -, #.
        - Пиши обычным текстом, без списков.
        """

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPEN_ROUTER_API}",
            },
            json={
                "model": "google/gemma-3-4b-it:free",
                "messages": [{"role": "user", "content": prompt}],
            }
        )

    return r.json()["choices"][0]["message"]["content"]
