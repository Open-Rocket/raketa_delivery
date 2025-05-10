# import logging

# # ANSI-коды цветов
# COLORS = {
#     "RESET": "\033[0m",  # Сброс цвета
#     "DEBUG": "\033[94m",  # Синий
#     "INFO": "\033[30m",  # сСерый
#     "WARNING": "\033[93m",  # Жёлтый
#     "ERROR": "\033[91m",  # Красный
#     "CRITICAL": "\033[41m",  # Красный фон
# }


# class ColoredFormatter(logging.Formatter):
#     def format(self, record) -> str:
#         """Форматирование лог-записи с учётом цвета"""

#         log_color = COLORS.get(record.levelname, COLORS["RESET"])
#         log_message = super().format(record)
#         return f"{log_color}{log_message}{COLORS['RESET']}"


# # Настраиваем логгер
# log = logging.getLogger()
# log.setLevel(logging.INFO)

# # Хэндлер для консоли
# handler = logging.StreamHandler()
# handler.setLevel(logging.INFO)

# # Применяем цветной форматтер
# formatter = ColoredFormatter("\n%(asctime)s - %(levelname)s: %(message)s\n")
# handler.setFormatter(formatter)

# log.addHandler(handler)

# __all__ = ["log"]


import logging

# Настраиваем логгер
log = logging.getLogger()
log.setLevel(logging.INFO)

# Хэндлер для консоли
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

# Простой формат без цветов и управляющих символов
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)

# Добавляем хэндлер (только один раз)
if not log.handlers:
    log.addHandler(handler)

__all__ = ["log"]
