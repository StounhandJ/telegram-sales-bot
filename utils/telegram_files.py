import os
from PIL import Image

from loader import bot
from data.config import notFoundDocument, notFoundImg

images_extension = [".png", ".jpeg", ".jpg"]


class TelegramFilesClass:

    def __init__(self):
        self.main_path = f"{os.path.dirname(os.path.abspath(__file__))}\..\data\\"
        self.uploaded_files = {}

    async def get_telegram_key_files(self, path, chatID):
        IsImage = os.path.splitext(self.main_path + path)[1] in images_extension
        file_id = ""
        if os.path.isfile(self.main_path + path) and (
                (not IsImage and self.document_size(os.stat(self.main_path + path).st_size)) or
                (IsImage and self.photo_size(os.stat(self.main_path + path).st_size) and
                 self.image_aspect_ratio(Image.open(self.main_path + path).width,
                                         Image.open(self.main_path + path).height))
        ):
            file_id = await self._uploading_image(path, chatID) if IsImage else await self._uploading_document(path,
                                                                                                               chatID)
        else:
            file_id = await self._uploading_image(notFoundImg, chatID) if IsImage else await self._uploading_document(
                notFoundDocument, chatID)
        return file_id

    async def _uploading_image(self, path, chatID):
        fileId = await self._get_uploaded_file(path)
        if fileId:
            return fileId
        else:
            send_file = await bot.send_photo(chat_id=chatID, photo=open(self.main_path + path, "rb"))
            await self._add_uploaded_file(path, send_file.photo[0].file_id)
            await send_file.delete()
            return send_file.photo[0].file_id

    async def _uploading_document(self, path, chatID):
        fileId = await self._get_uploaded_file(path)
        if fileId:
            return fileId
        else:
            send_file = await bot.send_document(chat_id=chatID, document=open(self.main_path + path, "rb"))
            await self._add_uploaded_file(path, send_file.document.file_id)
            await send_file.delete()
            return send_file.document.file_id

    async def _get_uploaded_file(self, path):
        file = self.uploaded_files.get(path)
        return file.get("file_id") if file and int(os.stat(self.main_path + path).st_mtime) == file.get(
            "last_modified") else None

    async def _add_uploaded_file(self, path, file_id):
        self.uploaded_files[path] = {"file_id": file_id, "last_modified": int(os.stat(self.main_path + path).st_mtime)}

    @staticmethod
    def document_size(size):
        return size < 51380224

    @staticmethod
    def photo_size(size):
        return size < 10485760

    @staticmethod
    def image_aspect_ratio(width, height):
        return round(width / height, 2) < 2.001 and round(height / width, 2) < 2.001


TelegramFiles = TelegramFilesClass()
