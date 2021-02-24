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

    def mkdir_department(self, departmentName):
        try:
            self.disk.mkdir(f"{self.path_main}/{departmentName}")
        except:
            print(f"YandexDisk Error: {departmentName} Данный отдел уже создан")

    def mkdir_staffer(self, stafferID, departmentName):
        try:
            if self.get_department(departmentName):
                self.disk.mkdir(f"{self.path_main}/{departmentName}/{stafferID}")
            else:
                print(f"YandexDisk Error: {departmentName} Данный отдел не создан")
        except:
            print(f"YandexDisk Error: {stafferID} Данный сотрудник уже добавлен в {departmentName}")

    def rename_department(self, departmentNameOld, departmentNameNew):
        try:
            self.disk.mkdir(f"/{self.path_main}/{departmentNameNew}/")
        except:
            print(f"YandexDisk Error: {departmentNameNew} Данный отдел уже создан")
            return
        self.disk.cp(f"/{self.path_main}/{departmentNameOld}/", f"/{self.path_main}/{departmentNameNew}/")
        time.sleep(2)
        self.disk.rm(f"{self.path_main}/{departmentNameOld}")


YandexDisk = YandexDiskClass()
