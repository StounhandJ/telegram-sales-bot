from utils.db_api.db import DataBase


class PromoCode:

    def __init__(self, id, name, code, percent, discount, limitation_use, count):
        self.id = id
        self.name = name
        self.code = code
        self.percent = percent
        self.discount = discount
        self.limitation_use = limitation_use
        self.count = count

    def save(self):
        return DataBase.request(
            "UPDATE `promo_codes` SET `name`=%(name)s,`code`=%(code)s,`percent`=%(percent)s,`discount`=%(discount)s,`count`=%(count)s WHERE `id`=%(id)s",
            {"name": self.name, "code": self.code, "percent": self.percent, "discount": self.discount, "count": self.count, "id": self.id})


def create_promo_code(name, code, percent, discount, limitation_use, count):
    return DataBase.request(
        "INSERT INTO `promo_codes`(`name`, `code`, `percent`, `discount`,`limitation_use`,`count`) VALUES (%(name)s,%(code)s,%(percent)s,%(discount)s,%(limitation_use)s,%(count)s)",
        {"name": name, "code": code, "percent": percent, "discount": discount, "limitation_use": limitation_use,
         "count": count})


def get_promo_code_id(id):
    response = DataBase.request(
        "SELECT `id`, `name`, `code`,`percent`, `discount`,`limitation_use`,`count` FROM `promo_codes` WHERE `id`=%(id)s",
        {"id": id})
    promo_code = None
    if response["code"] == 200:
        promo_code = PromoCode(response["data"]["id"], response["data"]["name"], response["data"]["code"],
                               response["data"]["percent"],
                               response["data"]["discount"], response["data"]["limitation_use"],
                               response["data"]["count"])
    return promo_code


def get_promo_code(code):
    response = DataBase.request(
        "SELECT `id`, `name`, `code`, `percent`, `discount`,`limitation_use`,`count` FROM `promo_codes` WHERE `code`=%(code)s",
        {"code": code})
    promo_code = None
    if response["code"] == 200:
        promo_code = PromoCode(response["data"]["id"], response["data"]["name"], response["data"]["code"],
                               response["data"]["percent"],
                               response["data"]["discount"], response["data"]["limitation_use"],
                               response["data"]["count"])
    return promo_code


def get_promoCode(page=0, max_size=10):
    response = DataBase.request(
        "SELECT `id`, `name`, `code`, `percent`, `discount`,`limitation_use`,`count` FROM `promo_codes` LIMIT %(page)s,%(max_size)s",
        {"page": page * max_size, "max_size": max_size})
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    promo_codes = []
    for code in response["data"]:
        promo_codes.append(PromoCode(code["id"], code["name"], code["code"], code["percent"],
                                     code["discount"], code["limitation_use"], code["count"]))
    return promo_codes


def get_ALLPromoCode():
    response = DataBase.request(
        "SELECT `id`, `name`, `code`, `percent`, `discount`,`limitation_use`,`count` FROM `promo_codes`")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    promo_codes = []
    for code in response["data"]:
        promo_codes.append(PromoCode(code["id"], code["name"], code["code"], code["percent"],
                                     code["discount"], code["limitation_use"], code["count"]))
    return promo_codes


def get_ALLPromoCode_count():
    response = DataBase.request("SELECT COUNT(`id`) AS 'count' FROM `promo_codes`")
    return response["data"]["count"] if response["code"] == 200 else 0


def promo_code_used(code):
    return DataBase.request(
        "UPDATE `promo_codes` SET `count`=`count`-1 WHERE `code`=%(code)s AND `limitation_use`=1 AND `count`>0",
        {"code": code})


def promo_code_not_used(code):
    return DataBase.request(
        "UPDATE `promo_codes` SET `count`=`count`+1 WHERE `code`=%(code)s AND `limitation_use`=1",
        {"code": code})


def delete_promo_code(id):
    return DataBase.request("DELETE FROM `promo_codes` WHERE `id`=%(id)s", {"id": id})
