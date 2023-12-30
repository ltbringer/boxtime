import sys
from loguru import logger

config = {
    "handlers": [
        {
            "format": "{time}|{name}:{line}|{function}| {message}",
        },
        {"sink": "debug.log", "serialize": True},
    ],
}

logger.configure(**config)
logger.enable("boxtime")
