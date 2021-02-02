from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminMesUser(StatesGroup):
    message = State()
    wait = State()
