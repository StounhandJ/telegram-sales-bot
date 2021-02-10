import json

from utils.db_api import db


def create_department(name, tag):
    try:
        db.DataBase.request(
            """INSERT INTO `department`(`name`, `staff`, `tag`) VALUES ("{name}",'[]',"{tag}")""".format(
                name=name, tag=tag))
        return {"success": True}
    except:
        return {"success": False}


def get_all_departments():
    try:
        out = []
        for var in db.DataBase.request(
                """SELECT `id`, `name`, `staff`, `tag` FROM `department`"""):
            out.append({"id": int(var[0]), "name": var[1], "staff": json.loads(var[2]), "tag": var[3]})
        return {"success": out != [], "data": out}
    except:
        return {"success": False}


def get_department_id(id):
    try:
        response = db.DataBase.request(
            """SELECT `id`, `name`, `staff`, `tag` FROM `department` WHERE `id`={id}""".format(
                id=id))[0]
        return {"success": True, "id": int(response[0]), "name": response[1],
                "staff": json.loads(response[2]), "tag": response[3]}
    except:
        return {"success": False}


def get_department(tag):
    try:
        response = db.DataBase.request(
            """SELECT `id`, `name`, `staff`, `tag` FROM `department` WHERE `tag`="{tag}" """.format(
                tag=tag))[0]
        return {"success": True, "id": int(response[0]), "name": response[1],
                "staff": json.loads(response[2]), "tag": response[3]}
    except:
        return {"success": False}


def update_department(departmentID, name, tag):
    try:
        db.DataBase.request("""UPDATE `department` SET `name`="{name}", `tag`="{tag}" WHERE `id`={id}""".format(
            name=name, tag=tag, id=departmentID))
        return {"success": True}
    except:
        return {"success": False}


def delete_department(id):
    try:
        db.DataBase.request("""DELETE FROM `department` WHERE `id`={id}""".format(id=id))
        return {"success": True}
    except:
        return {"success": False}


def add_staff(departmentID, userID):
    try:
        staff = get_department_id(departmentID)["staff"]
        staff.append(int(userID))
        db.DataBase.request("""UPDATE `department` SET `staff`='{staff}' WHERE `id`={id}""".format(
            staff=json.dumps(staff), id=departmentID))
        return {"success": True}
    except:
        return {"success": False}


def del_staff(departmentID, userID):
    try:
        staff = get_department_id(departmentID)["staff"]
        staff.remove(userID)
        db.DataBase.request("""UPDATE `department` SET `staff`='{staff}' WHERE `id`={id}""".format(
            staff=json.dumps(staff), id=departmentID))
        return {"success": True}
    except:
        return {"success": False}
