from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio



from LOGGING.LoggerConfig import logger
from states.states import *

from handlers.Combo import setcombo
from handlers.Admin import *
from handlers.Journal.Journal import journal
from handlers.Homework.Homework import choose_viewhomework, insert_subject
from handlers.Simple import choose_floor_miusi, schedule
from handlers.UserSave.UserSave import start



# Exception Router
er = Router()

commaddict = {
    '/start' : 'start(message)',
    '/viewhomework' : 'choose_viewhomework(message, session)',
    '/sethomework' : 'insert_subject(message, state, session)',
    '/journal' : 'journal(message, session, state)',
    '/map'  : 'choose_floor_miusi(message, state)',
    '/combo'  : 'setcombo(message, state)',
    '/schedule' : 'schedule(message, session)'
}

@er.message(StateFilter('*'), F.text.startswith('/'))
async def exc(message: Message, state: FSMContext, session: AsyncSession):
    current_state = await state.get_state()
    if current_state is not None:
        try:
            await state.clear()
            await eval(commaddict[message.text])
        except Exception as e:
            await message.answer(text=f'<b>Извини, но такой команды не существует</b>\n\nЛучше воспользуйся менюшкой слева')
            logger.debug(f'У пользователя {message.from_user.username} возникла ошибка при смене состояния: {e}')
    else:
        if message.text not in commaddict.keys():
            await message.answer(text=f'<b>Извини, но такой команды не существует</b>\n\nЛучше воспользуйся менюшкой слева')
        else:
            pass       