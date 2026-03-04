import logging
import sys
from app.config import settings


def setup_logging():
    """
    Настраивает логирование для всего приложения
    """
    # Создаем формат для логов
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Настраиваем вывод в консоль (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)

    # Определяем уровень логирования в зависимости от окружения
    if settings.environment == "development":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Также настроим логгер для нашего приложения
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    app_logger.addHandler(console_handler)
    app_logger.propagate = False  # Предотвращаем дублирование

    # Отключаем лишние логи от библиотек (опционально)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return app_logger


# Создаем глобальный экземпляр логгера
logger = logging.getLogger("app")