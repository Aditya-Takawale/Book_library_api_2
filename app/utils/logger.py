import logging
from app.config import settings
import datetime

def setup_logger():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'logs/app_{datetime.datetime.now().strftime("%Y%m%d")}.log')
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()