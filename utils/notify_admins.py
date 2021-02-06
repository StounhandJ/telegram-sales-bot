import logging

from data.config import ADMINS

from loader import dp


async def on_startup_notify():
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Бот Запущен")

        except Exception as err:
            logging.exception(err)


async def notify_admins_message(mes):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, mes)

        except Exception as err:
            logging.exception(err)