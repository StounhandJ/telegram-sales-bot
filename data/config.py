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
    "code_missing": "Данного промокода нет",
    "comment_order": "Оставьте коментарий к заказу: ",
    "comment_promoCode": "Введите промокод:",
    "comment_promoCodeCheck": "У вас есть промокод?",
    "code_info": "Название: {name}\nСкидка: {discount}",
    "promoCode_confirmation": "Ваш промокод:\n{text}",
    "comment_confirmation": "Ваш текст:\n{text}",
    "comment_confirmation_yes": "Заявка отправлена",
    "comment_confirmation_no": "Напишите ваш новый коментарий к заказу:",
    "product_missing": "Извените, но данный товар больше нельзя заказать",
    "message_sent": "Сообщение отправллено администрации",
    "message_no": "Напишите свое сообщение ещё раз: ",
    "message_cancel": "Отправка сообщения администрации отменена.",
    "Coursework": "Шаблон для курсовой\n***********\n*************\n**********\nНапишите вашу заявку соответственно шаблону:",
    "Diploma": "Шаблон для дипломной\n***********\n*************\n**********\nНапишите вашу заявку соответственно шаблону:"
}

adminMessage = {
    "help": "/orderspr - Все заявки в расмотрение\n/infopr orderProID - Подробная информация о заказе на рассмотрении\n/sendr orderProID - отправить форму оплаты\n/closer - Отказать в заказе(не работает)"
            "/orders - Выведет все заказы\n/info orderID - Информация о заказе\n/orderClose orderID - Закрыт заказ\n/send orderID - Начать ввод сообщений для отправки заказчику\n"
            "/codeList - Список всех товаров\n/codeAdd - Начать создание новго промокода\n/codeEdit codeID - Изменить промокод\n/ordermes or /allmes - Просмотреть все входящие сообщения\n"
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
    "price_send": "Напишите сумму оплаты",
    "document_add": "Документ добавлен",
    "img_add": "Изображение добавлено",
    "mes_add": "Сообщение добавлено",
    "code_main": "Список промокодов:\n",
    "codes_missing": "Промокодов нет",
    "code_missing": "Данного промокода нет",
    "code_info": "{num}. ID прмокода <b>{id}</b>\nНазвание: {name}\nСкидка: {discount}\n\n",
    "code_edit": "/name: {name}\n/code: {code}\n/type: {typeD}\n/discount: {discount}\nУдалить промокод /delete\nОтменить изменения /back\n",
    "code_add_name": "Укажите название:",
    "code_add_code": "Напишете промокод:",
    "code_add_percent": "Скидка в процентах или суммой(1-сумма,2-процент):",
    "code_add_discount": "Укажите скидку(число):",
    "code_add_confirmation": "Правильно?",
    "code_add_repeat": "Повторите: ",
    "code_add_cancel": "Создание промокода отменено",
    "code_edit_back": "Меню изменений промокода закрыто",
    "code_del_yes": "Промокод удален",
    "code_del_no": "Удаление прмокода отменено",
    "messages_missing": "Сообщений нет",
    "message_missing": "Данного сообщения нет",
    "messages_info": "{num}. Номер сообщения <b>{id}</b> от {date}\n",
    "message_detailed_info": "Номер сообщения <b>{id}</b>\nТекст: {text}\nДата отправки: {date}\n",
    "message_completed": "На данное сообщение уже ответили",
    "message_cancel": "Отправка сообщения пользователю отменена",
    "messages_main_order": "Список сообщений от покупателей:\n",
    "messages_main_all": "Список сообщений от обычныйх пользователей:\n",
    "order_pr_detailed_info": "Номер заказа <b>{orderID}</b>\nТекст заявки:\n{text}\nСкидка: {discount}\nДата заказа: {date}\n",
    "price_confirmation": "Отправить форму оплаты?"
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
