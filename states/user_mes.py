from aiogram.dispatcher.filters.state import StatesGroup, State


class UserMes(StatesGroup):
    message = State()
    wait = State()