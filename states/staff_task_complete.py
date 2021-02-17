from aiogram.dispatcher.filters.state import StatesGroup, State


class TaskComplete(StatesGroup):
    description = State()
    document = State()
    wait = State()
