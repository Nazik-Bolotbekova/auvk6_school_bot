import os

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
REQUEST_TOPIC_ID = int(os.getenv("REQUEST_TOPIC_ID"))
PROBLEM_TOPIC_ID = int(os.getenv("PROBLEM_TOPIC_ID"))
OPEN_ROUTER_API = os.getenv("OPEN_ROUTER_API")