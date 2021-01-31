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
    "help": "/orders - Выведет все заказы\n/info orderID - Информация о заказе\n/orderClose orderID - Закрыт заказ\n/send orderID - Начать ввод сообщений для отправки заказчику\n"
            "/productList - Список всех товаров\n/addProduct - Начать создание новго товара\n/productEdit productID - Изменить товар",
    "orders_main": "Список заказов:\n",
    "orders_missing": "Заказов нет",
    "order_missing": "Данного заказа нет",
    "order_completed": "Данный заказ уже выполнен",
    "order_close": "Закак с ID <b>{id}</b> был закрыт",
    "order_info": "{num}. Номер заказа <b>{orderID}</b> от {date}\n",
    "order_detailed_info": "Номер заказа <b>{orderID}</b>\nПредмет: {product}\nОплата: {price}\nКоментарий к заказу: {description}\n Дата заказа: {date}\n",
    "message_send": "Напишите сообщение для пользователя",
    "message_send_confirmation": "Проверить сообщение /mesCheck\nОтправить сообщение?",
    "message_yes_send": "Сообщение успешно отправленно пользователю",
    "message_not_send": "Отправка сообщения отменена",
    "document_add": "Документ добавлен",
    "img_add": "Изображение добавлено",
    "mes_add": "Сообщение добавлено",
    "products_main": "Список товаров:\n",
    "products_missing": "Товаров нет",
    "product_missing": "Данного товара нет",
    "product_info": "{num}. ID товара <b>{orderID}</b>\nНазвание: {name}\nЦена: {price}\nОписание: {description}\n\n",
    "product_edit": "/name: {name}\n/price: {price}\n/description: {description}\nОтменить изменения /back\n",
    "product_add_name": "Укажите название:",
    "product_add_description": "Укажите описание:",
    "product_add_price": "Укажите цену(числом):",
    "product_add_confirmation": "Подтвердить?",
    "product_add_repeat": "Повторите: ",
    "product_edit_back": "Меню изменений товара закрыто",
}

errorMessage = {
    "product_missing": "Данный предмет отсутвует"
}
