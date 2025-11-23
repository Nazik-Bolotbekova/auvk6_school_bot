import logging

logger = logging.getLogger("bot")              # логер
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("bot.log", mode='a')
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
)

logger.addHandler(file_handler)
