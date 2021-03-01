import json

from utils.db_api.db import DataBase
import time


def create_order(userID, description, document, price, separate_payment):
    return DataBase.request(
        "INSERT INTO `orders`( `userID`, `description`,`document`,`price` ,`date`,`active`, `separate_payment`) VALUES (%(userID)s,%(description)s,%(document)s,%(price)s,%(date)s,1,%(separate_payment)s)",
        {"userID": userID, "description": description, "document": json.dumps(document), "price": price,
         "date": int(time.time()), "separate_payment": separate_payment})


def get_order(id):
    return DataBase.request(
        "SELECT `id`,`userID`,`description`,`document`,`price`,`active`,`date`,`separate_payment`,`payment_key` FROM `orders` WHERE `id`=%(id)s",
        {"id": id})


def get_order_paymentKey(payment_key):
    return DataBase.request(
        "SELECT `id`,`userID`,`description`,`document`,`price`,`active`,`date`,`separate_payment`,`payment_key` FROM `orders` WHERE `payment_key`=%(payment_key)s",
        {"payment_key": payment_key})


def get_orders(page=0, max_size=10):
    response = DataBase.request(
        "SELECT `id`,`userID`,`date` FROM `orders` WHERE `active`=1 AND`active`=1 LIMIT %(page)s,%(max_size)s",
        {"page": page * max_size, "max_size": max_size})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_ALLOrders():
    response = DataBase.request("SELECT `id`,`userID`,`date` FROM `orders` WHERE `active`=1")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_ALLOrders_count():
    response = DataBase.request("SELECT COUNT(`id`) AS 'count' FROM `orders` WHERE `active`=1")
    return response["data"]["count"] if response["code"] == 200 else 0


def set_paymentKey_order(orderID, payment_key):
    return DataBase.request("UPDATE `orders` SET `payment_key`=%(payment_key)s WHERE `id`=%(id)s",
                            {"payment_key": payment_key, "id": orderID})


def updateSeparate_order(orderID):
    return DataBase.request("UPDATE `orders` SET `separate_payment`=0, `payment_key`='' WHERE `id`=%(id)s", {"id": orderID})


def updateActive_order(orderID):
    return DataBase.request("UPDATE `orders` SET `active`=0 WHERE `id`=%(id)s", {"id": orderID})
