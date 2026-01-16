import logging.config

from pathlib import Path

current_file_path = Path(__file__)
target_dir = current_file_path.parent.parent.parent
target_file_path = target_dir / "logs" / "ledsockets-server.log"
target_file_path2 = target_dir / "logs" / "ledsockets-client.log"

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
            "filename": target_file_path,
            "formatter": "cust",
            "maxBytes": 1000000,
            "backupCount": 5
        },
        "file2": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": target_file_path2,
            "formatter": "cust",
            "maxBytes": 1000000,
            "backupCount": 5
        }
    },
    "loggers": {
        "ledsockets.server": {
            "handlers": ["stdout", "file"], "level": "DEBUG"
        },
        "ledsockets.client": {
            "handlers": ["stdout", "file2"], "level": "DEBUG"
        }
    },
}

logging.config.dictConfig(LOGGING)


def get_logger(name):
    return logging.getLogger(name)
