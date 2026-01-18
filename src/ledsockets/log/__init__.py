import logging.config
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

current_file_path = Path(__file__)
target_dir = current_file_path.parent.parent.parent.parent
target_dirpath = target_dir / "logs"

IS_DEVELOPMENT = os.getenv('APP_ENV', 'production').lower() == 'local'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
MAX_BYTES = 0 if IS_DEVELOPMENT else 1000000
FILE_MODE = "w" if IS_DEVELOPMENT else "a"
if os.getenv('LOG_FILE_MODE'):
    FILE_MODE = os.getenv('LOG_FILE_MODE')

# @todo: configure base/root logger
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "cust": {
            "format": "[%(asctime)s][%(process)d] %(name)-27s %(levelname)8s - %(message)s",
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "cust",
        },
        "fileAll": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_dirpath / "ledsockets.log",
            "formatter": "cust",
            "backupCount": 5,
            "maxBytes": MAX_BYTES,
            "mode": FILE_MODE
        },
        "fileServer": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_dirpath / "ledsockets-server.log",
            "formatter": "cust",
            "backupCount": 5,
            "maxBytes": MAX_BYTES,
            "mode": FILE_MODE
        },
        "fileClient": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_dirpath / "ledsockets-client.log",
            "formatter": "cust",
            "backupCount": 5,
            "maxBytes": MAX_BYTES,
            "mode": FILE_MODE
        },
        "fileBoard": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_dirpath / "ledsockets-board.log",
            "formatter": "cust",
            "backupCount": 5,
            "maxBytes": MAX_BYTES,
            "mode": FILE_MODE
        },
    },
    "loggers": {
        "ledsockets": {
            "handlers": ["stdout", "fileAll"], "level": LOG_LEVEL
        },
        "ledsockets.board": {
            "handlers": ["fileBoard"], "level": LOG_LEVEL
        },
        "ledsockets.server": {
            "handlers": ["fileServer"], "level": LOG_LEVEL
        },
        "ledsockets.client": {
            "handlers": ["fileClient"], "level": LOG_LEVEL
        }
    },
}

logging.config.dictConfig(LOGGING)


def get_logger(name):
    return logging.getLogger(name)
