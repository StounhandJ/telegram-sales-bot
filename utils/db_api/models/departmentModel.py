import json

from utils.db_api.db import DataBase


class Department:

    def __init__(self, id, name, tag, staff):
        self.id = id
        self.name = name
        self.tag = tag
        self.staff = staff

    def save(self):
        return DataBase.request(
            "UPDATE `department` SET `name`=%(name)s, `tag`=%(tag)s, `staff`=%(staff)s WHERE `id`=%(departmentID)s",
            {"name": self.name, "tag": self.tag, "staff": json.dumps(self.staff), "departmentID": self.id})


def create_department(name, tag):
    return DataBase.request("INSERT INTO `department`(`name`, `staff`, `tag`) VALUES (%(name)s,'[]',%(tag)s)",
                            {"name": name, "tag": tag})


def get_all_departments():
    response = DataBase.request("SELECT `id`, `name`, `staff`, `tag` FROM `department`")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    departments = []
    for department in response["data"]:
        departments.append(Department(department["id"], department["name"], department["tag"], department["staff"]))
    return departments


def get_department_id(id):
    response = DataBase.request("SELECT `id`, `name`, `staff`, `tag` FROM `department` WHERE `id`=%(id)s", {"id": id})
    department = None
    if response["code"] == 200:
        department = Department(response["data"]["id"], response["data"]["name"], response["data"]["tag"],
                                response["data"]["staff"])
    return department


def get_department(tag):
    response = DataBase.request("SELECT `id`, `name`, `staff`, `tag` FROM `department` WHERE `tag`=%(tag)s", {"tag": tag})
    department = None
    if response["code"] == 200:
        department = Department(response["data"]["id"], response["data"]["name"], response["data"]["tag"],
                                response["data"]["staff"])
    return department


def get_all_staffs():
    response = DataBase.request("SELECT `id`, `name`, `staff`, `tag` FROM `department`")
    response["data"] = [response["data"]] if isinstance(response["data"], dict) else response["data"]
    staffs = []
    if response["code"] == 200:
        for department in response["data"]:
            staffs += department["staff"]
    return staffs


def delete_department(id):
    return DataBase.request("DELETE FROM `department` WHERE `id`=%(id)s", {"id": id})
