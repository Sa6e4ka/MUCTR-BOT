from aiogram.filters import Filter
from aiogram import types


class Admin_filt(Filter):
    def __init__(self, chat_id: list[str]):
        self.chat_id = chat_id

    async def __call__(self, message: types.Message):
        return message.chat.id in self.chat_id

