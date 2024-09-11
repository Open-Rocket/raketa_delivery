from aiogram.filters import Filter
from aiogram import types
import os
from dotenv import load_dotenv


ADMINS = [2045659349]


class AdminProtect(Filter):
    def __init__(self):
        self.admins = ADMINS

    async def __call__(self, message: types.Message):
        return message.from_user.id in self.admins
