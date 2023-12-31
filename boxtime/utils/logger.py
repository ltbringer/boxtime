from loguru import logger

config = {
    "handlers": [
        {
            "sink": "debug.log",
            "serialize": True,
            "level": "DEBUG",
            "format": "{time}|{name}:{line}|{function}| {message}",
        },
    ],
}

logger.configure(**config)
logger.enable("boxtime")
