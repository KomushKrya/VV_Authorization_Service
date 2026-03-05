import logging
import sys
from app.config import settings


def setup_logging():
    """
    Настраивает логирование для всего приложения
    """
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)

    if settings.environment == "development":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    app_logger.addHandler(console_handler)
    app_logger.propagate = False

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return app_logger

logger = logging.getLogger("app")
