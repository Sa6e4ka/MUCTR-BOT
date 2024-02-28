from aiogram import Bot, Router
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command, StateFilter
from filters.chat_types import Admin_filt

from database.engine import drop_db
from LOGGING.LoggerConfig import logger
#Admin Router
ar = Router()

ar.message.filter(Admin_filt(6592529444))

@ar.message(StateFilter(None), Command('DROPDATABASE'))
async def drop(message: Message):
    await drop_db()
    logger.error('БАЗА ДАННЫХ ПОЛНОСТЬЮ ОЧИЩЕНА')
    await message.answer('База данных полностью очищена!')

@ar.message(StateFilter(None), Command('loggs'))
async def send_loggs(message: Message):
        file_list = ['LOGGING/DEBUG.txt','LOGGING/ERROR.txt']
        for file in file_list:
            try:
                file = BufferedInputFile.from_file(path=file)
                await message.answer_document(document=file)
            except Exception:
                name = file.split('/')[-1]
                await message.answer(f'Файл <b>{name}</b> пуст')
