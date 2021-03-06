from aiogram.utils.callback_data import CallbackData

buy_callback = CallbackData("buy", "id", "item_name", "price")

setting_callback = CallbackData("setting", "command", "type")

confirmation_callback = CallbackData("confirmation", "bool")

type_work_callback = CallbackData("type_work", "work")

action_callback = CallbackData("edit", "what_action", "id")

numbering_callback = CallbackData("numbering", "what_action", "number")
