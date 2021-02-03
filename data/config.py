from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
PAYMENT_TOKEN = env.str("PAYMENT_TOKEN")
currency = env.str("currency")
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
    "comment_confirmation_yes": "Заявка отправлена",
    "comment_confirmation_no": "Напишите ваш новый коментарий к заказу:",
    "product_missing": "Извените, но данный товар больше нельзя заказать",
    "message_sent": "Сообщение отправллено администрации",
    "message_no": "Напишите свое сообщение ещё раз: ",
    "message_cancel": "Отправка сообщения администрации отменена."
}

adminMessage = {
    "help": "/orders - Выведет все заказы\n/info orderID - Информация о заказе\n/orderClose orderID - Закрыт заказ\n/send orderID - Начать ввод сообщений для отправки заказчику\n"
            "/productList - Список всех товаров\n/addProduct - Начать создание новго товара\n/productEdit productID - Изменить товар\n/ordermes or /allmes - Просмотреть все входящие сообщения\n"
            "/mesinfo mesID - Информаци о входящем сообщение\n/usend mesID - Отправить сообщение в ответ",
    "orders_main": "Список заказов:\n",
    "orders_missing": "Заказов нет",
    "order_missing": "Данного заказа нет",
    "order_completed": "Данный заказ уже выполнен",
    "order_close": "Закак с ID <b>{id}</b> был закрыт",
    "order_info": "{num}. Номер заказа <b>{orderID}</b> от {date}\n",
    "order_detailed_info": "Номер заказа <b>{orderID}</b>\nПредмет: {product}\nОплата: {price}\nКоментарий к заказу: {description}\nДата заказа: {date}\n",
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
    "product_add_confirmation": "Отправить?",
    "product_add_repeat": "Повторите: ",
    "product_add_cancel": "Создание товара отменено",
    "product_edit_back": "Меню изменений товара закрыто",
    "messages_missing": "Сообщений нет",
    "message_missing": "Данного сообщения нет",
    "messages_info": "{num}. Номер сообщения <b>{id}</b> от {date}\n",
    "message_detailed_info": "Номер сообщения <b>{id}</b>\nТекст: {text}\nДата отправки: {date}\n",
    "message_completed": "На данное сообщение уже ответили",
    "message_cancel": "Отправка сообщения пользователю отменена",
    "messages_main_order": "Список сообщений от покупателей:\n",
    "messages_main_all": "Список сообщений от обычныйх пользователей:\n",
}

payMessage = {
    "title": "Заказ услуги",
    "description": "Тут нужно будет прописать описание"
}

errorMessage = {
    "product_missing": "Данный предмет отсутвует",
    "exceeded_time_pay": "Вы пытаетесь оплатить старый товар. Для вашей же безопасности повторите заказ.",
    "payment_missing": "Произашла ошибка, ваш заказ скорее всего потерян. Свяжитесь с администрацией бота /ames"
}
