import logging.config

from pathlib import Path

current_file_path = Path(__file__)
target_dir = current_file_path.parent.parent.parent
target_dirpath = target_dir / "logs"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "cust": {
            "format": "[%(asctime)s][%(process)d] %(name)s - %(levelname)s - %(message)s",
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "cust",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_dirpath / "ledsockets-server.log",
            "formatter": "cust",
            "maxBytes": 1000000,
            "backupCount": 5
        },
        "file2": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_dirpath / "ledsockets-client.log",
            "formatter": "cust",
            "maxBytes": 1000000,
            "backupCount": 5
        },
        "file3": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_dirpath / "ledsockets-board.log",
            "formatter": "cust",
            "maxBytes": 1000000,
            "backupCount": 5
        },
        "file4": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_dirpath / "ledsockets.log",
            "formatter": "cust",
            "maxBytes": 1000000,
            "backupCount": 5
        }
    },
    "loggers": {
        "ledsockets": {
            "handlers": ["stdout", "file4"], "level": "DEBUG"
        },
        "ledsockets.board": {
            "handlers": ["file3"], "level": "DEBUG"
        },
        "ledsockets.server": {
            "handlers": ["file"], "level": "DEBUG"
        },
        "ledsockets.client": {
            "handlers": ["file2"], "level": "DEBUG"
        }
    },
}

logging.config.dictConfig(LOGGING)


def get_logger(name):
    return logging.getLogger(name)
