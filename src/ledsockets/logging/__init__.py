import logging.config

from pathlib import Path

current_file_path = Path(__file__)
target_dir = current_file_path.parent.parent.parent.parent

target_dirpath = target_dir / "logs"

IS_DEVELOPMENT = True
MAX_BYTES = 1000000

maxBytes = 0 if IS_DEVELOPMENT else MAX_BYTES
mode = "w" if IS_DEVELOPMENT else "a"
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
            "maxBytes": maxBytes,
            "mode": mode,
        },
        "fileServer": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_dirpath / "ledsockets-server.log",
            "formatter": "cust",
            "backupCount": 5,
            "maxBytes": maxBytes,
            "mode": mode,
        },
        "fileClient": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_dirpath / "ledsockets-client.log",
            "formatter": "cust",
            "backupCount": 5,
            "maxBytes": maxBytes,
            "mode": mode,
        },
        "fileBoard": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_dirpath / "ledsockets-board.log",
            "formatter": "cust",
            "backupCount": 5,
            "maxBytes": MAX_BYTES,
            "mode": "a"
        },
    },
    "loggers": {
        "ledsockets": {
            "handlers": ["stdout", "fileAll"], "level": "DEBUG"
        },
        "ledsockets.board": {
            "handlers": ["fileBoard"], "level": "DEBUG"
        },
        "ledsockets.server": {
            "handlers": ["fileServer"], "level": "DEBUG"
        },
        "ledsockets.client": {
            "handlers": ["fileClient"], "level": "DEBUG"
        }
    },
}

logging.config.dictConfig(LOGGING)


def get_logger(name):
    return logging.getLogger(name)
