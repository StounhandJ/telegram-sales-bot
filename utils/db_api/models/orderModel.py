from utils.db_api.db import DataBase
from utils.db_api.request import request


class Order:

    def __init__(self, id, userID, price, description, document, stateOfOrder, date):
        self.id = id
        self.userID = userID
        self.price = int(price / 100)
        self.description = description
        self.document = document
        self.active = stateOfOrder < 15
        self.payment = stateOfOrder < 10
        self.separate_payment = stateOfOrder == 12
        self.date = date

    def set_paymentKey_order(self, payment_key):
        return DataBase.request("UPDATE `orders` SET `payment_key`=%(payment_key)s WHERE `id`=%(id)s",
                                {"payment_key": payment_key, "id": self.id})

    def del_Separate_order(self):
        return DataBase.request("UPDATE `orders` SET `separate_payment`=0, `payment_key`='' WHERE `id`=%(id)s", {"id": self.id})

    def updateActive_order(self):
        return DataBase.request("UPDATE `orders` SET `active`=0 WHERE `id`=%(id)s", {"id": self.id})

    def priceSet(self, price):
        return request("POST", "/order.priceSet", {"id": self.id, "price": price})["data"]["price"]

    def chequeCreate(self, secretKey):
        return request("POST", "/order.chequeCreate", {"id": self.id, "secretKey": secretKey})["data"]


def get_order(id):
    response = request("GET", "/order", {"id": id})
    order = None
    if response["code"] == 200 and response["data"]["stateOfOrder"]>10:
        order = Order(response["data"]["id"], response["data"]["Client"]["telegramID"], response["data"]["price"], response["data"]["description"], response["data"]["document"]["documentTelegramId"], response["data"]["stateOfOrder"], response["data"]["date"])
    return order


def get_orders(page=0, max_size=10):
    response = request("GET", "/order.all", {"limit": max_size, "offset": page * max_size, "stateOfOrder": 11})
    response2 = request("GET", "/order.all", {"limit": max_size, "offset": page * max_size, "stateOfOrder": 12})
    orders = []
    for order in response["data"]:
        orders.append(
            Order(order["id"], order["Client"]["telegramID"], order["price"], order["description"], order["document"]["documentTelegramId"],
                  order["stateOfOrder"], order["date"]))
    for order in response2["data"]:
        orders.append(
            Order(order["id"], order["Client"]["telegramID"], order["price"], order["description"], order["document"]["documentTelegramId"],
                  order["stateOfOrder"], order["date"]))
    return orders


def get_ALLOrders():
    response = request("GET", "/order.all", {"stateOfOrder": 11})
    response2 = request("GET", "/order.all", {"stateOfOrder": 12})
    orders = []
    for order in response["data"]:
        orders.append(
            Order(order["id"], order["Client"]["telegramID"], order["price"], order["description"], order["document"]["documentTelegramId"],
                  order["stateOfOrder"], order["date"]))
    for order in response2["data"]:
        orders.append(
            Order(order["id"], order["Client"]["telegramID"], order["price"], order["description"], order["document"]["documentTelegramId"],
                  order["stateOfOrder"], order["date"]))
    return orders


def get_ALLOrders_count():
    response = request("GET", "/order.all", {"stateOfOrder": 11})
    response2 = request("GET", "/order.all", {"stateOfOrder": 12})
    responseLen = len(response["data"]) if response["code"] == 200 else 0
    response2Len = len(response2["data"]) if response2["code"] == 200 else 0
    return responseLen + response2Len

