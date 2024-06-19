__all__ = [
    "commands_for_bot",
]

from aiogram import types

bot_commands = (
    ("start", "Регистрация пользователя"),
    ("status", "Показать статус пользователя"),
    ("help", "Справка по боту"),
    ("register", "Инструкцию по регистрации на Яндекс Диске (только для преподавателей)"),
    ("token", "Ввод и проверка токена для Яндекс Диска (только для преподавателей)"),
    ("add", "Добавление папки в отслеживаемые для слушателей (только для преподавателей)"),
    ("delete", "Удаление папки из отслеживаемых для слушателей (только для преподавателей)")
)

commands_for_bot = []
for cmd in bot_commands:
    commands_for_bot.append(types.BotCommand(command=cmd[0], description=cmd[1]))
