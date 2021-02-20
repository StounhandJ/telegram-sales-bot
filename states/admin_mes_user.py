from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminMesUser(StatesGroup):
    message = State()
    document = State()
    documentCheck = State()
    wait = State()
