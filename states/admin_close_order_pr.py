from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminCloseOrderPr(StatesGroup):
    message = State()
    wait = State()
