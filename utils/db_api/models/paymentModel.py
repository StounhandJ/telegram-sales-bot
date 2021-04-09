from utils.db_api.request import request


class Payment:

    def __init__(self, id, amount, secret_key, date):
        self.id = id
        self.amount = amount
        self.secret_key = secret_key
        self.date = date

    def del_payment(self):
        request("POST", "/cheque.del", {"id": self.id})


def get_payment(secret_key):
    response = request("GET", "/cheque", {"secretKey": secret_key})
    payment = None
    if response["code"] == 200:
        payment = Payment(response["data"]["id"], response["data"]["amount"], response["data"]["secretKey"], response["data"]["date"])
    return payment


def paymentCompleted(secret_key):
    return request("POST", "/order.chequeCompleted", {"secretKey": secret_key})["code"]==200
