import os
from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
FILTER_GROUP_ID = os.getenv("FILTER_GROUP_ID")
OPEN_ROUTER_API = os.getenv("OPEN_ROUTER_API")


REQUEST_TOPIC_ID = int(os.getenv("REQUEST_TOPIC_ID") or "0")
PROBLEM_TOPIC_ID = int(os.getenv("PROBLEM_TOPIC_ID") or "0")


if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не установлен!")
if not OPEN_ROUTER_API:
    raise ValueError("❌ OPEN_ROUTER_API не установлен!")

print("Конфиг загружен")