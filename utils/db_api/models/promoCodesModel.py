from utils.db_api import db


def get_promo_code_id(id):
    try:
        response = db.DataBase.request(
            """SELECT `id`, `name`, `code`,`percent`, `discount` FROM `promo_codes` WHERE `id`={id}""".format(
                id=id))[0]
        return {"success": True, "id": int(response[0]), "name": response[1], "code": response[2], "percent": response[3],
                "discount": int(response[4])}
    except:
        return {"success": False}


def get_promo_code(code):
    try:
        response = db.DataBase.request(
            """SELECT `id`, `name`, `code`, `percent`, `discount` FROM `promo_codes` WHERE `code`="{code}" """.format(
                code=code))[0]
        return {"success": True, "id": int(response[0]), "name": response[1], "code": response[2], "percent": response[3],
                "discount": int(response[4])}
    except:
        return {"success": False}


def get_ALLPromoCode():
    try:
        out = []
        for var in db.DataBase.request("""SELECT `id`, `name`, `code`, `percent`, `discount` FROM `promo_codes`"""):
            out.append({"id": int(var[0]), "name": var[1], "code": var[2], "percent": var[3], "discount": int(var[4])})
        return {"success": True, "data": out}
    except:
        return {"success": False}


def create_promo_code(name, code, percent, discount):
    try:
        db.DataBase.request("""INSERT INTO `promo_codes`(`name`, `code`, `percent`, `discount`) VALUES ("{name}","{code}",{percent},{discount})""".format(
            name=name, code=code,percent=percent, discount=discount
        ))
        return {"success": True}
    except:
        return {"success": False}


def update_promo_code(id, name, code, percent, discount):
    try:
        db.DataBase.request("""UPDATE `promo_codes` SET `name`="{name}",`code`="{code}",`percent`={percent},`discount`={discount} WHERE `id`={id}""".format(
            id=id, name=name, code=code, percent=percent, discount=discount
        ))
        return {"success": True}
    except:
        return {"success": False}


def delete_promo_code(id):
    try:
        db.DataBase.request("""DELETE FROM `promo_codes` WHERE `id`={id}""".format(id=id))
        return {"success": True}
    except:
        return {"success": False}