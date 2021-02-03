from aiogram.dispatcher.filters.state import StatesGroup, State


class ProductEdit(StatesGroup):
    zero = State()
    name = State()
    description = State()
    price = State()
