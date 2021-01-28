from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста

message = {
    "About_Us": "Текст для информации \"о нас\"",
    "Product_Menu": "Товары",
    "Main_Menu": "Главное меню",
    "Welcome_Menu": "Тут сообщение приветствия",
    "product_info": "Предмет: {item_name}\nЦена: {price}",
    "comment_order": "Оставьте коментарий к заказу: ",
    "comment_confirmation": "Ваш текст:\n{text}",
    "comment_confirmation_yes": "Заявка отправлена(позже тут сначала оплата будет)",
    "comment_confirmation_no": "Напишите ваш новый коментарий к заказу:",
}
