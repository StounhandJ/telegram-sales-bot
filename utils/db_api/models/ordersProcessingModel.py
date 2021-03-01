import json

from utils.db_api.db import DataBase
import time


def create_order_provisional(userID, text, document, separate_payment, percent, discount):
    return DataBase.request(
        "INSERT INTO `orders_processing`(`userID`, `text`, `document` ,`active`, `separate_payment`, `percent`, `discount`, `date`) VALUES (%(userID)s,%(text)s,%(document)s,1,%(separate_payment)s,%(percent)s,%(discount)s,%(date)s)",
        {"userID": userID, "text": text, "document": json.dumps(document), "separate_payment": separate_payment,
         "percent": percent, "discount": discount,
         "date": int(time.time())})


def get_order_provisional(id):
    return DataBase.request(
        "SELECT `id`, `userID`, `text`, `document`, `active`, `separate_payment`, `percent`, `discount`, `date` FROM `orders_processing` WHERE `id`=%(id)s",
        {"id": id})


def get_orders_provisional(page=0, max_size=10):
    response = DataBase.request(
        "SELECT `id`,`userID`,`date` FROM `orders_processing` WHERE `active`=1 AND`active`=1 LIMIT %(page)s,%(max_size)s",
        {"page": page * max_size, "max_size": max_size})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_ALLOrders_provisional_count():
    response = DataBase.request("SELECT COUNT(`id`) AS 'count' FROM `orders_processing` WHERE `active`=1")
    return response["data"]["count"] if response["code"] == 200 else 0


def updateActive_order(id):
    return DataBase.request(
        "UPDATE `orders_processing` SET `active`=0 WHERE `id`=%(id)s",
        {"id": id})
