from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("ip")
dbUSER = env.str("dbUSER")
dbPASSWORD = env.str("dbPASSWORD")
DATABASE = env.str("DATABASE")

message = {
    "About_Us": "Текст для информации \"о нас\"",
    "Product_Menu": "Товары",
    "Main_Menu": "Главное меню",
    "Welcome_Menu": "Тут сообщение приветствия",
    "product_info": "Предмет: {item_name}\nОписание: {description}\nЦена: {price}",
    "comment_order": "Оставьте коментарий к заказу: ",
    "comment_confirmation": "Ваш текст:\n{text}",
    "comment_confirmation_yes": "Заявка отправлена(позже тут сначала оплата будет)",
    "comment_confirmation_no": "Напишите ваш новый коментарий к заказу:",
}

adminMessage = {
    "order_main": "Список заказов:\n",
    "order_missing": "Заказов нет",
    "order_info": "{num}. Номер заказа <b>{orderID}</b> от {date}\n",
    "order_detailed_info": "Номер заказа <b>{orderID}</b>\nПредмет: {product}\nОплата: {price}\nКоментарий к заказу: {description}\n Дата заказа: {date}\n",
}

errorMessage = {
    "product_missing": "Данный предмет отсутвует"
}
