from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminPriceOrder(StatesGroup):
    price = State()
    wait = State()
