from utils.db_api.db import DataBase


def get_promo_code_id(id):
    return DataBase.request(
        "SELECT `id`, `name`, `code`,`percent`, `discount`,`limitation_use`,`count` FROM `promo_codes` WHERE `id`=%(id)s",
        {"id": id})


def get_promo_code(code):
    return DataBase.request(
        "SELECT `id`, `name`, `code`, `percent`, `discount`,`limitation_use`,`count` FROM `promo_codes` WHERE `code`=%(code)s",
        {"code": code})


def get_ALLPromoCode():
    response = DataBase.request(
        "SELECT `id`, `name`, `code`, `percent`, `discount`,`limitation_use`,`count` FROM `promo_codes`")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def create_promo_code(name, code, percent, discount, limitation_use, count):
    return DataBase.request(
        "INSERT INTO `promo_codes`(`name`, `code`, `percent`, `discount`,`limitation_use`,`count`) VALUES (%(name)s,%(code)s,%(percent)s,%(discount)s,%(limitation_use)s,%(count)s)",
        {"name": name, "code": code, "percent": percent, "discount": discount, "limitation_use": limitation_use,
         "count": count})


def promo_code_used(code):
    return DataBase.request(
        "UPDATE `promo_codes` SET `count`=`count`-1 WHERE `code`=%(code)s AND `limitation_use`=1 AND `count`>0",
        {"code": code})


def promo_code_not_used(code):
    return DataBase.request(
        "UPDATE `promo_codes` SET `count`=`count`+1 WHERE `code`=%(code)s AND `limitation_use`=1",
        {"code": code})


def update_promo_code(id, name, code, percent, discount, count):
    return DataBase.request(
        "UPDATE `promo_codes` SET `name`=%(name)s,`code`=%(code)s,`percent`=%(percent)s,`discount`=%(discount)s,`count`=%(count)s WHERE `id`=%(id)s",
        {"name": name, "code": code, "percent": percent, "discount": discount, "count": count, "id": id})


def delete_promo_code(id):
    return DataBase.request("DELETE FROM `promo_codes` WHERE `id`=%(id)s", {"id": id})
