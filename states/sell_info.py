from aiogram.dispatcher.filters.state import StatesGroup, State


class SellInfo(StatesGroup):
    description = State()
