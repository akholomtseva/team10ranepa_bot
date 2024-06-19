__all__ = [
    "register_message_handler",
]


import logging

from aiogram import Router, F
from aiogram import types
from aiogram.filters.command import Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import TOKEN_URL
from db import async_session_maker, User
from db.models import YandexDiskFolder
from yandex import YandexFunctions
from .callbacks import start_callback
from .keyboards import registerbutton


async def help_command(message: types.Message):
    help_str = """Вас приветствует бот <b><i>Проверка обновлений яндекс диска</i></b>
    💬 Регистрация пользователя <b>/start</b>
    💬 Информацию о пользователе можно вывести с помощью команды <b>/status</b>"""

    logging.info(f"user {message.from_user.id} asked for help")
    await message.reply(text=help_str, parse_mode="HTML")


async def status_command(message: types.Message):
    """Информация о пользователе"""

    async with async_session_maker() as session:
        session: AsyncSession

        user = await session.get(User, message.from_user.id)
        await session.close()

        if user is None:
            await message.reply(text="Вы не зарегистрированы")
        else:
            text = f"""<b>Ваше имя</b>: <i>{user.name}</i>\n<b>Ваш ID</b>: <i>{user.id}</i>\n"""

            await message.reply(text=text, parse_mode="HTML")

        logging.info(f"user {message.from_user.id} requested status")


async def start_command(message: types.Message):
    async with async_session_maker() as session:
        session: AsyncSession

        user = await session.get(User, message.from_user.id)

        await session.close()

        if user is None:
            await message.reply("Выберите роль:", reply_markup=registerbutton)
        else:
            await message.reply(f"Вы уже зарегестрированы")

        logging.info(f"user {message.from_user.id} started the bot")


async def register_user_command(message: types.Message):
    id = int(message.text)
    async with async_session_maker() as session:
        session: AsyncSession

        teacher = await session.get(User, id)

        if teacher is None:
            await message.answer("Преподаватель с таким ID не найден")
        else:
            new_user = User(id=message.from_user.id, user_teacher_id=id, name=message.from_user.username)
            session.add(new_user)
            await session.commit()
            await session.close()

            await message.answer(f"Вы зарегистрировались как слушатель")

        logging.info(f"user {message.from_user.id} registered as a student")


async def register_command(message: types.Message):
    text = (f"Для регистрации токена следуйте шагам:\n"
    f"1. Перейдите по ссылке: <a href=\"{TOKEN_URL}\">{TOKEN_URL}</a>\n"
    f"2. Авторизируйтесь.\n"
    f"3. Скопируйте ТОКЕН и вставьте его в <b>/token ТОКЕН</b>.")

    await message.reply(text=text, parse_mode="HTML")

    logging.info(f"user {message.from_user.id} requested token registration instructions")


async def token_command(message: types.Message):
    async with async_session_maker() as session:
        session: AsyncSession

        user = await session.get(User, message.from_user.id)

        if user is None:
            await message.reply("Для добавления токена зарегистрируйтесь как преподаватель")
        elif user.user_teacher_id:
            await message.reply("Вы не преподаватель")
        else:
            message_split = message.text.split()

            if len(message_split) < 2:
                if user.token:
                    await message.reply(f"{user.token}")
                else:
                    await message.reply("Введите токен после команды через пробел /token")
            else:
                token = message_split[1].strip()

                client = YandexFunctions(token=token)
                yes = await client.check_token()

                if yes:
                    user.token = token
                    await session.commit()

                    await message.reply(f"Токен обновлен")
                else:
                    await message.reply(f"Неправильный токен")

        logging.info(f"user {message.from_user.id} requested token command")


async def add_command(message: types.Message):
    async with async_session_maker() as session:
        session: AsyncSession

        message_split = message.text.split()

        if len(message_split) < 2:
            await message.reply("Укажите название или путь к папке через пробел после /add")
        else:
            name = message.text.split()[1].strip()

            user = await session.get(User, message.from_user.id)

            if not user:
                await message.reply("Вы не зарегистрированы")
            elif user.user_teacher_id:
                await message.reply("Вы не преподаватель")
            elif not user.token:
                await message.reply("У Вас нет токена")
            else:
                new = YandexDiskFolder(user_teacher_id=user.id, name=name)
                session.add(new)

                await session.commit()
                await session.close()

                await message.reply(f"Папка '{name}' добавлена")

        logging.info(f"user {message.from_user.id} asked for added a folder")


async def delete_command(message: types.Message):
    async with async_session_maker() as session:
        session: AsyncSession

        message_split = message.text.split()

        if len(message_split) < 2:
            await message.reply("Укажите название или путь к папке через пробел после /add")
        else:
            name = message.text.split()[1].strip()

            user = await session.get(User, message.from_user.id)

            if not user:
                await message.reply("Вы не зарегистрированы")
            elif user.user_teacher_id:
                await message.reply("Вы не преподаватель")
            elif not user.token:
                await message.reply("У Вас нет токена")
            else:
                # ? поиск по совпадению айди и названию папки
                stmt = select(YandexDiskFolder).filter(YandexDiskFolder.user_teacher_id is user.id, YandexDiskFolder.name is name)
                result = await session.execute(stmt)
                folder = result.scalars().first()

                if not folder:
                    await message.reply("Папка не найдена")
                    return

                await session.delete(folder)
                await session.commit()

                await message.reply(f"Папка '{name}' удалена")

            logging.info(f"user {message.from_user.id} asking for deleted a folder")


def register_message_handler(router: Router):
    """Маршрутизация"""
    router.message.register(start_command, Command(commands=["start"]))
    router.message.register(register_command, Command(commands=["register"]))
    router.message.register(status_command, Command(commands=["status"]))
    router.message.register(token_command, Command(commands=["token"]))
    router.message.register(help_command, Command(commands=["help"]))
    router.message.register(add_command, Command(commands=["add"]))
    router.message.register(delete_command, Command(commands=["delete"]))
    router.message.register(register_user_command)
    router.callback_query.register(start_callback, F.data.startswith("reg_"))