from aiogram.dispatcher.filters.state import StatesGroup, State


class ProductAdd(StatesGroup):
    name = State()
    description = State()
    price = State()
