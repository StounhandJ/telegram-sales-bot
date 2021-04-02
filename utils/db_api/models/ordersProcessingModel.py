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

    def calculate_price(self, price, secretKey):
        return request("POST", "/order.calculate", {"id": self.id, "price": price, "secretKey": secretKey})["data"]["price"]

    def set_state_wait(self):
        request("POST", "/order.update", {"id": self.id, "stateOfOrder": 0})



def create_order_provisional(userID, text, typeWork, promoCodeID, document, separate_payment):
    request("POST", "/order.create", {"idClient": userID, "description": text, "typeWork": typeWork,
                                      "stateOfOrder": 1, "docTelegID": document, "promoCodeID": promoCodeID,
                                      "separate": 1 if separate_payment else 0,
                                      "otherDiscount": 0 if separate_payment else discount_full_payment})


def get_order_provisional(id):
    response = request("GET", "/order", {"id": id})
    order = None
    if response["code"] == 200:
        document = response["data"]["document"]["documentTelegramId"] if response["data"]["document"] else None
        responsePayment = request("GET", "/paymentOrder.all", {"idOrder": id})
        otherDiscount = 0
        promoCodeInfo = "0р."
        if responsePayment["code"] == 200:
            otherDiscount = responsePayment["data"][0]["otherDiscount"]
            promoCodeInfo = request("GET", "/promocode", {"id": responsePayment["data"][0]["promoCodeID"]})["data"][
                "info"] if responsePayment["data"][0]["promoCodeID"] else promoCodeInfo
        order = OrderProvisional(response["data"]["id"], response["data"]['idClient']['telegramID'],
                                 response["data"]["description"],
                                 document,
                                 response["data"]["stateOfOrder"] == 1, otherDiscount, promoCodeInfo,
                                 response["data"]["date"])
    return order


def get_orders_provisional(page=0, max_size=10):
    response = request("GET", "/order.all", {"limit": max_size, "offset": page * max_size, "stateOfOrder": 1})
    orders = []
    for order in response["data"]:
        orders.append(
            OrderProvisional(order["id"], order['idClient']['telegramID'], "", None, True, 0, "", order["date"]))
    return orders


def get_ALLOrders_provisional_count():
    response = request("GET", "/order.all", {"stateOfOrder": 1})
    return len(response["data"]) if response["code"] == 200 else 0
