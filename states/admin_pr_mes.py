from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminPrMes(StatesGroup):
    message = State()
    wait = State()
