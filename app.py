from aiogram import executor
import threading

from loader import dp
import middlewares, handlers
from utils.notify_admins import on_startup_notify
import backup


async def on_startup(dispatcher):
    # Уведомляет про запуск
    middlewares.setup(dp)
    await on_startup_notify()


if __name__ == '__main__':
    backup_process = threading.Thread(target=backup.backup)
    backup_process.start()
    executor.start_polling(dp, on_startup=on_startup)
