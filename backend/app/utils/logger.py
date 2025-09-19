
import logging
from logging.handlers import RotatingFileHandler
import datetime
import os
from app.config import settings

def setup_logger():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("BookLibraryAPI")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler = RotatingFileHandler(
        f"{log_dir}/app_{datetime.datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()