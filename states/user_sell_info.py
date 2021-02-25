from aiogram.dispatcher.filters.state import StatesGroup, State


class SellInfo(StatesGroup):
    description = State()
    email = State()
    documentCheck = State()
    document = State()
    promoCodeCheck = State()
    separatePayment = State()
    promoCode = State()
    wait = State()
