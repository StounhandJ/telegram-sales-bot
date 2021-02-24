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
DISK_LOGIN = env.str("DISK_LOGIN")
DISK_PASSWORD_APP = env.str("DISK_PASSWORD_APP")

discount_full_payment = 5  # Скидка при полной оплате сразу


works = {"Курсовая": {
        "description": "Цена работы может варьироваться от 3000 р.\nЖелательно предоставление методических материалов по КП.",
        "template": "Шаблон заявки оформления курсовой работы<i>\nПредмет:\nЗаголовок:\nТекст заявки:\nЖелаемые сроки выполнения:\nПрикреплённые файлы:</i>\nНапишите вашу заявку соответственно шаблону:"
    },
    "Дипломная": {
        "description": "Цена работы может варьироваться от 7000 р.\nЖелательно предоставление методических материалов по ДП",
        "template": "Шаблон заявки оформления дипломной работы\n<i>Предмет:\nЗаголовок:\nТекст заявки:\nЖелаемые сроки выполнения:\nПрикреплённые файлы:</i>\nНапишите вашу заявку соответственно шаблону:"
    },
    "3D Печать":
        {
        "description": "<i>Мы выполняем печать 3D моделей по технологии FDM</i>",
        "template": "3D Печать\nЦена:\nABS - от 15р-гр\nPLA - от 10р-гр\nHIPS - от 9р-гр\nPETG - от 15р-гр\nSBS - от 12р-гр\nSBS GLASS - от 15р-гр\nTPU - от 13р-гр\n\nОбычная печать от 3-х рабочих дней\nСерийная печать от 7-и рабочих дней\nДля оказания услуги укажите следующие параметры:\n\nФайл.stl(Если моделей несколько, то назовите их  в виде: 1.stl и укажите количество ниже)\nКоличество\nКачество\nЖелаемый срок исполнения\nТип пластика(Если делаете заказ на 2 и более моделей с разным видом пластика, то пропишите это дополнительно для каждой модели в zip архиве в названии каждого файла, а здесь укажите два типа пластика)"
    },
    "Моделирование":
        {
        "description": "Мы выполняем моделирование объектов в программах: <i>Blender, SolidWorks, Inventor cad, TinkerCad, 3d max, </i>",
        "template": "<b>Моделирование</b>Оценивается согласно поставленному Техническому заданию.\n\nУкажите следующие параметры:\n\nНеобходимые входные данные для реализации модели\nОписание необхоимой 3д модели\nЭскиз, визуализация идеи\nЧертежи(При наличии)\nФайл или ZIP архив для дополнительной информации\nЖелаемый срок реализации"
    },
    "Дизайн":
        {
        "description": "Работа выполняется по договорённости, в соответствии с Техническим заданием.",
        "template": "Цена выполнения зависит от сложности работы и от необходимиого конечного продукта.\n\nПросим вас предоставить подробное описание требуемого дизайна ниже с указанием срока исполнения:"
    },
    "Разработка Embedded систем":
        {
        "description": "Производится реализация устройства от идеи до конечного прототипа.",
        "template": "Срок выполнения: <i>от 7 рабочих дней</i>.\nЦена устанавливается в соответствии с установленным техническим заданием.\n\nПожалуйста, опишите ваш заказ согласно следующим данным:\nНеобходимое итоговое оборудование\nФункционал оборудования\nПлафторма реализации(ARM, AVR или x86)\nКоличество\nЕсли у вас есть другие данные по разработке, то укажите их здесь\nФайл или архив ZIP c чертажами, datasheet и прочей информацией\nЖелаемый срок реализации"
    }
}
message = {
    "About_Us": "Neproblemka.ru - <i>сервис по решению ваших проблем в короткие сроки.</i>\nNeproblemka.ru: <b>Ваша проблема - наше решение.</b>",
    "Product_Menu": "На данный момент мы выполняем:<b>\n\t\tКурсовые работы\n\t\tДипломные работы\n\t\t3D печать\n\t\tМоделирование\n\t\tДизайн\n\t\tРазработка Embedded систем и прототипирование устройств</b>",
    "Main_Menu": "Главное меню",
    "Welcome_Menu": "Добрый день. Чего желаете?",
    "product_info": "Предмет: <i>{item_name}</i>\nОписание: <i>{description}</i>\nЦена: <i>{price}</i>",
    "code_missing": "Данного промокода не существует",
    "comment_order": "Оставьте коментарий к заказу: ",
    "comment_documentCheck": "Есть дополнительный файл?",
    "comment_document": "Прикрепите файл, если у вас несколько файлов добавьте архив:",
    "comment_promoCodeCheck": "Имеется ли у вас промокод?",
    "comment_promoCode": "Введите промокод:",
    "separatePayment": "Хотите оплатить всю сумму сразу? При оплате сразу скидка 5%. Иначе оплата будет по частям.",
    "promoCode_confirmation": "Ваш промокод:\nНазвание: {name}\nСкидка: {discount}",
    "document_confirmation": "Ваш документ:\n{text}",
    "comment_confirmation": "Ваш текст:\n\n{text}",
    "comment_confirmation_yes": "<b>Оплата прошла успешно</b>, ваша заявка отправлена на выполнение, ожидайте",
    "comment_confirmation_no": "Повторите:",
    "product_missing": "Извините, но данный товар больше нельзя заказать",
    "message_sent": "<b>Сообщение отправлено администрации</b>",
    "message_no": "Напишите свое сообщение ещё раз: ",
    "message_cancel": "Отправка сообщения администрации отменена.",
    "order_complete": "<b>Вам сообщение от администратора</b> по поводу вашего заказа:",
    "order_close": "Ваш <b>заказ был выполнен</b> и закрыт",
    "order_send": "Ваша заявка принята",

    "orderPR_denied": "<b>Вам отказано</b> в заказе, коментарий к отказу:\n",

    "increased_requests": "Вы превысили количество обращений в день",
    "repeat_requests": "Вы недавно отпраили сообщение.\nПовторное можно будет отправить через <b>{min}</b> минут",

    "report_mes": "Напишите свое сообщение:",
}

adminMessage = {
    "help": "Команды:/akeyboard - Включить клавиатуру администратора\n/banList - Список забаненных\n/ban |userID| - Добавить человека в бан\n/unban |userID| - Удалить человека из бана\n/departmentAdd - Создание отдела\n/infod |tag| - Информация о отделе"
            "\n/departmentEdit |tag| - Редактирования отдела\n/infomes |mesID| - Информация о сообщении\n/info |orderID| - Информация о оплаченном заказе\n/infopr |PRorderID| - Информация о заказе на рассмотрении"
            "\n/codeAdd - Создание промокода\n/codeEdit |codeID| - Редактирование промокода\n/set_task |tag| |orderID| |messages| - Создание задачи для отделов (tag= @diz or @diz.2)"
            "\n/task_list - Список выданных задач\n/all_result |orderID| - Информация о всех результатах работы по данному заказу",
    "ordersPR_main": "Список заказов:\n{text}\n/infopr orderProID - Подробная информация о заказе на рассмотрении",
    "orders_main": "Список заказов:\n{text}\n/info orderID - Информация о заказе",
    "orders_missing": "Заказов нет",
    "order_missing": "Данного заказа нет",
    "order_completed": "Данный заказ уже выполнен",
    "order_confirm": "Закрыть заказ?\n(Отправить ответ на заказ надо перед закрытием)",
    "order_confirm_no": "Закрытие заказа отменено",
    "order_close": "Закак с ID <b>{id}</b> был закрыт",
    "order_info": "{num}. Номер заказа <b>{orderID}</b> от {date}\n",
    "order_detailed_info": "Номер заказа <b>{orderID}</b>\nОплата: {price}\nОплачена <b>{payment}</b>\nКоментарий к заказу: {description}\nДата заказа: {date}\n",
    "order_close_text": "Напишите текст для отказа:",
    "order_close_confirm": "Отправить отказ?",

    "message_send": "Напишите сообщение для пользователя",
    "message_send_confirmation": "Проверить сообщение /mesCheck\nОтправить сообщение?",
    "message_yes_send": "Сообщение успешно отправленно пользователю",
    "message_not_send": "Отправка сообщения отменена",
    "price_send": "Укажите сумму оплаты",
    "document_add": "Документ добавлен",
    "img_add": "Изображение добавлено",
    "mes_add": "Сообщение добавлено",

    "code_main": "Список промокодов:\n{text}\n/codeAdd - Добавить новый промокод\n/codeEdit |codeID| - Изменить промокод",
    "codes_missing": "Промокодов нет",
    "code_missing": "Данного промокода нет",
    "code_info": "{num}. ID прмокода <b>{id}</b>\nНазвание: {name}\nКоличество: {count}\nСкидка: {discount}\n\n",
    "code_edit": "Название: {name}\nКод: {code}\n Количество: {count}\nСкидка: {discount}",
    "code_add_name": "Укажите название:",
    "code_add_code": "Напишите промокод:",
    "code_add_percent": "Скидка в процентах или суммой:",
    "code_add_discount": "Укажите скидку (Число):",
    "code_add_confirmation": "Правильно?",
    "code_add_repeat": "Повторите: ",
    "code_add_cancel": "Создание промокода отменено",
    "code_del_yes": "Промокод удален",

    "messages_main": "{start}\n{text}\n/mesinfo - информация о сообщении",
    "messages_missing": "Сообщений нет",
    "message_missing": "Данного сообщения нет",
    "messages_info": "{num}. Номер сообщения <b>{id}</b> от {date}\n",
    "message_detailed_info": "Номер сообщения <b>{id}</b>\nID отправителя <b>{userID}</b>\nТекст: {text}\nДата отправки: {date}\n",
    "message_completed": "На данное сообщение уже ответили",
    "messages_main_order": "Список сообщений от покупателей:\n",
    "messages_main_all": "Список сообщений от обычных пользователей:\n",

    "order_pr_detailed_info": "Номер заказа <b>{orderID}</b>\nID заказчика <b>{userID}</b>\nТекст заявки:\n{text}\nСкидка: {discount}\nОплата <b>{payment}</b>\nДата заказа: {date}\n",
    "price_confirmation": "Отправить форму оплаты?",
    "admin_mes_order_provisional": "<b>Новый</b> заказ, нужно его рассмотреть и дать хорошую цену ; )\n/orderspr",
    "admin_mes_order_paid": "<b>Оплачен</b> новый заказа, надо бы его сделать\n/orders",
    "admin_mes_order_paid_two": "<b>Оплачена</b> вторая часть заказа <b>{orderID}</b>, надо бы его сделать\n/orders",

    "departments_missing": "Отделов нет",
    "department_missing": "Данный отдел не существует",
    "departments_main": "Отделы:<i>\n{text}</i>\nКоманды:/infod |tag|\n/departmentEdit |tag|\n/departmentAdd",
    "department_info": "{num}. Название отдела: {name}\nТэг: @{tag}\nКоличество сотрудников: {count_staff}\n\n",
    "department_detailed_info": "Название отдела: {name}\nТэг: @{tag}\nСотрудники: {count_staff}",
    "department_add_name": "Укажите название отдела",
    "department_add_tag": "Укажите тэг для отдела (Пример: admin)",
    "department_add_user": "Укажите ID пользователя чтобы добавить его",
    "department_del_user": "Укажите ID пользователя чтобы удалить его",
    "department_edit": "Название {name}\n@{tag}",
    "department_edit_no": "Изменение отменено",
    "department_edit_back": "Меню изменений отдела закрыто",
    "department_del_yes": "Отдел удален",
    "department_del_no": "Удаление отдела отменено",

    "new_task_staff": "Вам поставленна новая задача /task_list",
    "task_list_missing": "Задачи не установлены",
    "task_list_main": "Задачи:\n{text}\n/set_task staff orderID mes\n/all_result orderID",
    "task_list_info": "Номер заказа <b>{orderID}</b>\nКоличество людей в работе: {staff}\n\n",
    "task_result_missing": "Результатов по данной работе нет",
    "task_result_main": "Результаты:\n{text}",
    "task_result_info": "{number}. @{department} {user} ({userID})\n\n",
}

departmentMessage = {
    "task_list_missing": "У вас нет задач",
    "task_main": "Список ваших задач:\n",
    "task_button": "Заказ номер {}",
    "task_info": "Номер заказа <b>{orderID}</b>\nКоментарий к заказу: {description}\nКоментарий от админа: {descriptionA}",
    "task_add_comment": "Напишите коментарий к работе:",
    "task_add_document": "Прикрепите документ или архив с работой",
    "task_send": "Ответ отправлен",
}

payMessage = {
    "title": "Заказ услуги",
    "description": "UnderConstr",
    "payment_two": "Нужно <b>оплатить вторую часть работы</b>."
}

errorMessage = {
    "not_add_photo": "Если вы хотете прикрепить фото добавьте его например в архив и отправьте",
    "exceeded_time_pay": "Вы пытаетесь оплатить старый товар. Для вашей же безопасности повторите заказ.",
    "payment_missing": "Произашла ошибка, ваш заказ скорее всего потерян. Свяжитесь с администрацией бота /ames"
}
