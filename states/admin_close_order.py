from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminCloseOrder(StatesGroup):
    wait = State()
