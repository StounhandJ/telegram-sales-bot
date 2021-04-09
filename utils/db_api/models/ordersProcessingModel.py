from data.config import discount_full_payment
from utils.db_api.request import request


class OrderProvisional:

    def __init__(self, id, userID, text, document, active, otherDiscount, promoCodeInfo, date):
        self.id = id
        self.userID = userID
        self.text = text
        self.document = document
        self.active = active
        self.otherDiscount = otherDiscount
        self.promoCodeInfo = promoCodeInfo
        self.date = date

    def updateActive_order(self):
        request("POST", "/order.del", {"id": self.id})

    def priceSet(self, price):
        return request("POST", "/order.priceSet", {"id": self.id, "price": price})["data"]["price"]

    def chequeCreate(self, secretKey):
        request("POST", "/order.chequeCreate", {"id": self.id, "secretKey": secretKey})


def create_order_provisional(idClient, text, typeWork, promoCodeID, document, separate_payment):
    request("POST", "/order.create", {"idClient": idClient, "description": text, "typeWork": typeWork,
                                      "stateOfOrder": 1, "docTelegID": document, "promoCodeID": promoCodeID,
                                      "separate": 1 if separate_payment else 0,
                                      "otherDiscount": 0 if separate_payment else discount_full_payment})


def get_order_provisional(id):
    response = request("GET", "/order", {"id": id})
    order = None
    if response["code"] == 200:
        document = response["data"]["document"]["documentTelegramId"] if response["data"]["document"] else None
        promoCodeInfo = "0р."
        otherDiscount = response["data"]["otherDiscount"]
        promoCodeInfo = request("GET", "/promocode", {"id": response["data"]["promoCodeID"]})["data"][
                "info"] if response["data"]["promoCodeID"] else promoCodeInfo
        order = OrderProvisional(response["data"]["id"], response["data"]['idClient']['telegramID'],
                                 response["data"]["description"],
                                 document,
                                 response["data"]["stateOfOrder"] == 0, otherDiscount, promoCodeInfo,
                                 response["data"]["date"])
    return order


def get_orders_provisional(page=0, max_size=10):
    response = request("GET", "/order.all", {"limit": max_size, "offset": page * max_size, "stateOfOrder": 0})
    orders = []
    for order in response["data"]:
        orders.append(
            OrderProvisional(order["id"], order['idClient']['telegramID'], "", None, True, 0, "", order["date"]))
    return orders


def get_ALLOrders_provisional_count():
    response = request("GET", "/order.all", {"stateOfOrder": 1})
    return len(response["data"]) if response["code"] == 200 else 0
