import os
import time

from YaDiskClient.YaDiskClient import YaDisk
from data import config


class YandexDiskClass:

    def __init__(self):
        self.path_main = "TelegramBOT"
        self.disk = YaDisk(config.DISK_LOGIN, config.DISK_PASSWORD_APP)
        elements = self.disk.ls("/")
        for element in elements:
            if element['isDir'] and element['displayname'] == self.path_main:
                return
        self.disk.mkdir(self.path_main)

    def get_departments(self):
        return self.disk.ls(self.path_main)

    def get_department(self, departmentName):
        try:
            return self.disk.ls(f"{self.path_main}/{departmentName}")
        except:
            return None

    def get_staffer(self, stafferID, departmentName):
        try:
            return self.disk.ls(f"{self.path_main}/{departmentName}/{stafferID}")
        except:
            return None

    def get_order_staffer(self,orderID ,stafferID, departmentName):
        try:
            return self.disk.ls(f"{self.path_main}/{departmentName}/{stafferID}/{orderID}")
        except:
            return None

    def mkdir_department(self, departmentName):
        try:
            self.disk.mkdir(f"{self.path_main}/{departmentName}")
        except:
            print(f"YandexDisk Error: <{departmentName}> Данный отдел уже создан")

    def mkdir_staffer(self, stafferID, departmentName):
        try:
            if self.get_department(departmentName):
                self.disk.mkdir(f"{self.path_main}/{departmentName}/{stafferID}")
            else:
                print(f"YandexDisk Error: <{departmentName}> Данный отдел не создан")
        except:
            print(f"YandexDisk Error: <{stafferID}> Данный сотрудник уже добавлен в <{departmentName}>")

    def mkdir_order(self, orderID, stafferID, departmentName):
        try:
            if self.get_staffer(stafferID, departmentName):
                self.disk.mkdir(f"{self.path_main}/{departmentName}/{stafferID}/{orderID}")
            else:
                print(f"YandexDisk Error: В <{departmentName}> этом отделе нет сотрудника <{stafferID}>")
        except:
            print(f"YandexDisk Error: <{orderID}> Данный заказ уже добавлен сотруднику <{stafferID}> отдела <{departmentName}>")

    def rename_department(self, departmentNameOld, departmentNameNew):
        try:
            self.disk.mkdir(f"/{self.path_main}/{departmentNameNew}/")
        except:
            print(f"YandexDisk Error: <{departmentNameNew}> Данный отдел уже создан")
            return
        self.disk.cp(f"/{self.path_main}/{departmentNameOld}/", f"/{self.path_main}/{departmentNameNew}/")
        time.sleep(2)
        self.disk.rm(f"{self.path_main}/{departmentNameOld}")

    def add_file(self, stafferID, departmentName, orderID, file):
        if not self.get_department(departmentName):
            print(f"YandexDisk Error: <{departmentName}> Данный отдел не создан")
            return
        if not self.get_staffer(stafferID, departmentName):
            self.mkdir_staffer(stafferID, departmentName)
        if not self.get_order_staffer(orderID, stafferID, departmentName):
            self.mkdir_order(orderID, stafferID, departmentName)
        elements_path = file.split('/')
        file_name = elements_path[len(elements_path)-1]
        self.disk.upload(file, f"/{self.path_main}/{departmentName}/{stafferID}/{orderID}/{file_name}")


YandexDisk = YandexDiskClass()
