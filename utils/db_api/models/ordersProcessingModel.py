import json

from utils.db_api.db import DataBase
import time


def create_order_provisional(userID, text, document, percent, discount):
    return DataBase.request(
        "INSERT INTO `orders_processing`(`userID`, `text`, `document` ,`active`, `percent`, `discount`, `date`) VALUES (%(userID)s,%(text)s,%(document)s,1,%(percent)s,%(discount)s,%(date)s)",
        {"userID": userID, "text": text, "document": json.dumps(document), "percent": percent, "discount": discount,
         "date": int(time.time())})


def get_order_provisional(id):
    return DataBase.request(
        "SELECT `id`, `userID`, `text`, `document`, `active`, `percent`, `discount`, `date` FROM `orders_processing` WHERE `id`=%(id)s",
        {"id": id})


def get_ALLOrders_provisional():
    response = DataBase.request("SELECT `id`,`userID`,`date` FROM `orders_processing` WHERE `active`=1")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def updateActive_order(id):
    return DataBase.request(
        "UPDATE `orders_processing` SET `active`=0 WHERE `id`=%(id)s",
        {"id": id})
