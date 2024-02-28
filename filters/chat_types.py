from aiogram.filters import Filter
from aiogram import types
from LOGGING.LoggerConfig import logger
from aiogram.fsm.context import FSMContext

class Admin_filt(Filter):
    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    async def __call__(self, message: types.Message, state: FSMContext):
        if message.chat.id == self.chat_id:
            return True
        else:
            current_state = await state.get_state()
            if current_state == None:
                logger.error(f'Пользователь {message.from_user.username} воспользовался командой {message.text} не будучи админом!')
                await message.answer('Ты только что воспользовался командой, пользоваться которой тебе не позволено 😑\n\n<b>Админ уже знает об этом и скоро тебя найдет 👿</b>')
                await state.clear()
                return False
            else:
                return True

