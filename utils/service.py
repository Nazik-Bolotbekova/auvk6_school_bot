import httpx
from aiogram.types import Message
from utils.bot_logconfig import logger
from config import REQUEST_TOPIC_ID, PROBLEM_TOPIC_ID, OPEN_ROUTER_API


def chunk_text(text: str, size: int = 4096):
    return [text[i:i+size] for i in range(0, len(text), size)]  # чанкер для отправки # большого текста


def log_location_chat(message: Message, action: str):
    username = message.from_user.username              # для логов (проверка чата либо лички)
    chat_id = message.chat.id
    if message.chat.type == 'private':
        logger.info(f'{username} {action} in PRIVATE chat')
    else:
        logger.info(f'{username} {action} in CHAT {chat_id} chat')


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




async def analyze_message(message_text: str):
    prompt = f"""
Ты — фильтр токсичности. Отвечай ТОЛЬКО JSON. 
Не пиши пояснений. Не используй markdown. 
Не используй тройные кавычки или блоки кода.

Если сообщение содержит:
- мат, оскорбления, токсичность
- агрессию или унижение
- негативные фразы о сотрудниках школы ("Елена Александровна Волошина", "Еленка", "Волошина", "Волошка")
- бессмысленный детский флуд

→ верни {{"analysis": "not_okay"}}

Если ничего такого нет:
→ верни {{"analysis": "okay"}}

Сообщение: "{message_text}"

Отвечай строго JSON и ничего больше.

Если ты получаешь фотку а не текст игнорируб
"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPEN_ROUTER_API}"},
            json={
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
            }
        )

    data = r.json()

    logger.debug("MODEL RAW DATA: %s", data)

    if "choices" not in data or not data["choices"]:
        logger.warning("Модель вернула пустой ответ или ошибку %s", data)
        return "model_failed"

    try:
        raw = data["choices"][0]["message"]["content"]
    except KeyError:
        return "model_failed"

    analysis = extract_analysis(raw)
    logger.info(f"DEBUG ANALYSIS -> user=%s text=%r {analysis}")
    return analysis


import json
import re

def extract_analysis(raw: str) -> str:
    logger.debug("extract_analysis raw=%r", raw)
    if not raw or not isinstance(raw, str):
        return "model_failed"
    try:
        match = re.search(r"\{.*?\}", raw, flags=re.S)
        if not match:
            logger.warning("JSON в raw не найден")
            return "model_failed"
        data = json.loads(match.group(0))
        analysis = data.get("analysis")
        if analysis in ("okay", "not_okay"):
            return analysis
        logger.warning("Неверный analysis: %r", analysis)
        return "model_failed"
    except Exception:
        logger.exception("Ошибка при парсинге raw")
        return "model_failed"
