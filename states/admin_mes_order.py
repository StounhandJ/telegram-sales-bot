from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminMesOrder(StatesGroup):
    message = State()
