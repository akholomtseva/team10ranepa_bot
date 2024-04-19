# Этап 1

# Дополнительный гайд по aiogram https://mastergroosha.github.io/aiogram-3-guide/quickstart/
# Дополнительный гайд по асинхронному бэкенду https://habr.com/ru/companies/kts/articles/598575/
# Дополнительный гайд по логированию https://habr.com/ru/companies/wunderfund/articles/683880/

# Установить библиотеки и фреймворки aiogram==3.4
# pip install aiogram
# pip install python-dotenv

# Для сохранения текущих пакетов в проекте и их версий при переносе используйте файл requirements.txt
# pip freeze — внешние пакеты проекта
# pip freeze > requirements.txt — сохранить внешние пакеты в файл
# pip install -r requirements.txt —  загрузить пакеты из файла


# импорты
import asyncio  # библиотека для асинхронного программирования
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config import TOKEN

# создание экземпляров классов Bot и Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()


# асинхронный вызов функции - конкурентный вызов с ожиданием события для продолжения процесса выполнения
@dp.message(Command('start'))
async def process_start_message(message: types.Message):
    """Приветствие"""
    await message.answer("Привет!")


@dp.message()
async def echo(message: types.Message):
    """Эхо-ответ"""
    await message.answer(message.text)


async def start():
    await dp.start_polling(bot)


# запуск бота через long_polling
if __name__ == "__main__":
    asyncio.run(start())