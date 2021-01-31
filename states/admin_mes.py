from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminMes(StatesGroup):
    message = State()
