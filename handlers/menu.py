from aiogram import F, Bot, Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_querry import orm_add_combo, orm_get_combo_comp
from LOGGING.LoggerConfig import logger

from states.states import СomboState  


#combo Router
cr = Router()

# Обработчик команды /setmenu
@cr.message(StateFilter(None), Command('setmenu'))
async def setmenu(message: Message, state: FSMContext):
    await message.answer('Введи сегодняшнее меню столовой:')
    await state.set_state(СomboState.compound)


# Сохраняем меню
@cr.message(StateFilter(СomboState.compound), or_f(F.text, F.photo, F.video, F.sticker, F.voice, F.audio, F.document))
async def save_menu(message: Message, state: FSMContext, session: AsyncSession):
    if message.text:
        await message.answer('Меню успешно сохранено!\n\nТеперь ты и остальные пользователи бота могут посмотреть его по команде /menu')
        # Сохраняем меню
        await orm_add_combo(session=session, data=message.text)
        await state.clear()
    else:
        await state.clear()
        await message.answer('Пожалуйста, введи состав текстом!')
        await state.set_state(СomboState.compound)

# Обработчик команды /menu для просмотра меню
@cr.message(Command('menu'))
async def view_menu(message: Message, session: AsyncSession):
    try:
        # Получаем из таблички данные о комбо (состав[0] и цена[1])
        compound = await orm_get_combo_comp(session=session)
        if compound != None:
            await message.answer(text=f'Меню столовой в общаге на сегодня:\n\n{compound}\n\n<b>Если меню не сегодняшнее, то самое время его обновить --> /setmenu</b>')
        else:
            await message.answer('Похоже, что меню пока что не ввели :(\n\nБудь первым --> /setmenu')
    except Exception as e:
        await message.answer('Похоже, что-то пошло не так :(\n\nОбязательно напиши об этом @NeBot100Proz')
        logger.debug(f'У {message.from_user.username} произошла ошибка при просмотре меню: {e}')