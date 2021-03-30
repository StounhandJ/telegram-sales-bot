from utils.db_api.db import DataBase
from utils.db_api.request import request


class PromoCode:

    def __init__(self, id, name, code, discount, typeOfCode, limitation_use, info):
        self.id = id
        self.name = name
        self.code = code
        self.discount = discount
        self.typeOfCode = typeOfCode
        self.limitation_use = limitation_use
        self.info = info

    def save(self):
        return request("POST", "/promocode.update", {"id": self.id, "name": self.name,
                                                     "codeName": self.code, "discount": self.discount,
                                                     "typeOfCode": self.typeOfCode, "limitUsing": self.limitation_use})


def create_promo_code(name, code, IsPercent, discount, count):
    return request("POST", "/promocode.create", {"name": name, "codeName": code,
                                                 "discount": discount, "typeOfCode": 1 if IsPercent else 0,
                                                 "limitUsing": count})


def get_promo_code_id(id):
    response = request("GET", "/promocode", {"id": id})
    promo_code = None
    if response["code"] == 200:
        promo_code = PromoCode(response["data"]["id"], response["data"]["name"], response["data"]["code"],
                               response["data"]["discount"],
                               response["data"]["typeOfCode"], response["data"]['limitUsing'], response["data"]['info'])
    return promo_code


def get_promo_code(code):
    response = request("GET", "/promocode", {"code": code})
    promo_code = None
    if response["code"] == 200:
        promo_code = PromoCode(response["data"]["id"], response["data"]["name"], response["data"]["code"],
                               response["data"]["discount"],
                               response["data"]["typeOfCode"], response["data"]['limitUsing'], response["data"]['info'])
    return promo_code


def get_promoCode(page=0, max_size=10):
    response = request("GET", "/promocode.all", {"limit": max_size, "offset": page * max_size})
    promo_codes = []
    for code in response["data"]:
        promo_codes.append(PromoCode(code["id"], code["name"], code["code"], code["discount"],
                                     code["typeOfCode"], code['limitUsing'], code['info']))
    return promo_codes


def get_ALLPromoCode():
    response = request("GET", "/promocode.all")
    promo_codes = []
    for code in response["data"]:
        promo_codes.append(PromoCode(code["id"], code["name"], code["code"], code["discount"],
                                     code["typeOfCode"], code['limitUsing'], code['info']))
    return promo_codes


def get_ALLPromoCode_count():
    response = request("GET", "/promocode.all")
    return len(response["data"]) if response["code"] == 200 else 0


def promo_code_used(code):
    return DataBase.request(
        "UPDATE `promo_codes` SET `count`=`count`-1 WHERE `code`=%(code)s AND `limitation_use`=1 AND `count`>0",
        {"code": code})


def promo_code_not_used(code):
    return DataBase.request(
        "UPDATE `promo_codes` SET `count`=`count`+1 WHERE `code`=%(code)s AND `limitation_use`=1",
        {"code": code})


def delete_promo_code(id):
    return request("POST", "/promocode.del", {"id": id})
