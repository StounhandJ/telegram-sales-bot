from aiogram.utils.callback_data import CallbackData

buy_callback = CallbackData("buy", "item_name", "price")

setting_callback = CallbackData("setting", "command")

confirmation_callback = CallbackData("confirmation", "bool")