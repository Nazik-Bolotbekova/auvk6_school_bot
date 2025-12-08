import logging
import sys
import psutil

logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)


formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)


file_handler = logging.FileHandler("bot.log", mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


async def log_resources():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024

    if memory_mb > 200:
        logger.warning(f"Высокое потребление памяти: {memory_mb:.2f} MB")

    logger.info(f"RAM: {memory_mb:.2f} MB | CPU: {process.cpu_percent()}%")