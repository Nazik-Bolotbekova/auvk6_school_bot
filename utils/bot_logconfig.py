import logging
import psutil

logger = logging.getLogger("bot")              # логер
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("bot.log", mode='a', encoding='utf-8')
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
)

logger.addHandler(file_handler)




async def log_resources():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024

    if memory_mb > 200:
        logging.warning(f"Высокое потребление памяти: {memory_mb:.2f} MB")

    logger.info(f"📊 RAM: {memory_mb:.2f} MB | CPU: {process.cpu_percent()}%")

