import json

from utils.db_api.db import DataBase


def create_department(name, tag):
    return DataBase.request("INSERT INTO `department`(`name`, `staff`, `tag`) VALUES (%(name)s,'[]',%(tag)s)",
                            {"name": name, "tag": tag})


def get_all_departments():
    response = DataBase.request("SELECT `id`, `name`, `staff`, `tag` FROM `department`")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    return response


def get_department_id(id):
    return DataBase.request("SELECT `id`, `name`, `staff`, `tag` FROM `department` WHERE `id`=%(id)s", {"id": id})


def get_department(tag):
    return DataBase.request("SELECT `id`, `name`, `staff`, `tag` FROM `department` WHERE `tag`=%(tag)s", {"tag": tag})


def update_department(departmentID, name, tag):
    return DataBase.request("UPDATE `department` SET `name`=%(name)s, `tag`=%(tag)s WHERE `id`=%(departmentID)s",
                            {"name": name, "tag": tag, "departmentID": departmentID})


def delete_department(id):
    return DataBase.request("DELETE FROM `department` WHERE `id`=%(id)s", {"id": id})


def add_staff(departmentID, userID):
    staff = get_department_id(departmentID)["data"]["staff"]
    staff.append(int(userID))
    return DataBase.request("UPDATE `department` SET `staff`=%(staff)s WHERE `id`=%(departmentID)s",
                            {"staff": json.dumps(staff), "departmentID": departmentID})


def del_staff(departmentID, userID):
    staff = get_department_id(departmentID)["data"]["staff"]
    staff.remove(userID)
    return DataBase.request("UPDATE `department` SET `staff`=%(staff)s WHERE `id`=%(departmentID)s",
                            {"staff": json.dumps(staff), "departmentID": departmentID})
