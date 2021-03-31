import json

from utils.db_api.db import DataBase
from data.config import discount_full_payment
from utils.db_api.request import request


class OrderProvisional:

    def __init__(self, id, userID, text, document, active, separate_payment, percent, discount, date):
        self.id = id
        self.userID = userID
        self.text = text
        self.document = document
        self.active = active
        self.separate_payment = separate_payment
        self.percent = percent
        self.discount = discount
        self.date = date

    def updateActive_order(self):
        return DataBase.request(
            "UPDATE `orders_processing` SET `active`=0 WHERE `id`=%(id)s",
            {"id": self.id})


def create_order_provisional(userID, text, typeWork, promoCodeID, document, separate_payment):
    order = request("POST", "/order.create", {"idClient": userID, "description": text, "typeWork": typeWork,
                                      "stateOfOrder": 1})

    request("POST", "/paymentOrder.create", {"idOrder": order["data"]["id"], "price": 0, "promoCodeID": promoCodeID,
                                             "otherDiscount": 0 if separate_payment else discount_full_payment})


def get_order_provisional(id):
    response = DataBase.request(
        "SELECT `id`, `userID`, `text`, `document`, `active`, `separate_payment`, `percent`, `discount`, `date` FROM `orders_processing` WHERE `id`=%(id)s",
        {"id": id})
    order = None
    if response["code"] == 200:
        order = OrderProvisional(response["data"]["id"], response["data"]["userID"], response["data"]["text"],
                                 response["data"]["document"],
                                 response["data"]["active"], response["data"]["separate_payment"],
                                 response["data"]["percent"], response["data"]["discount"], response["data"]["date"])
    return order


def get_orders_provisional(page=0, max_size=10):
    response = DataBase.request(
        "SELECT `id`,`userID`,`date` FROM `orders_processing` WHERE `active`=1 AND`active`=1 LIMIT %(page)s,%(max_size)s",
        {"page": page * max_size, "max_size": max_size})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    orders = []
    for order in response["data"]:
        orders.append(OrderProvisional(order["id"], order["userID"], "", [], True, False, False, 0, order["date"]))
    return orders


def get_ALLOrders_provisional_count():
    response = DataBase.request("SELECT COUNT(`id`) AS 'count' FROM `orders_processing` WHERE `active`=1")
    return response["data"]["count"] if response["code"] == 200 else 0
