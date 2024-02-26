from aiogram import F, Bot, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_querry import orm_add_combo, orm_get_combo_comp
from LOGGING.LoggerConfig import logger

from states.states import СomboState  


#combo Router
cr = Router()

# Обработчик команды /setcombo
@cr.message(StateFilter(None), Command('setcombo'))
async def setcombo(message: Message, state: FSMContext):
    await message.answer('Введи состав комбо-обеда:')
    await state.set_state(СomboState.compound)

# Обработчик снятия состояния 

# Сохраняем состав комбо
@cr.message(СomboState.compound, F.text)
async def SaveCombo(message: Message, bot: Bot, state: FSMContext):

        await state.update_data(compound = message.text)
        await message.answer('Cостав Комбо-обеда сохранен! Теперь введи его цену:')
        # Сохраняем в словарь состояния
        await state.set_state(СomboState.price)

# Сохраняем цену комбо
@cr.message(StateFilter(СomboState.price), F.text)
async def SaveCombo(message: Message, state: FSMContext, session: AsyncSession):        
    await state.update_data(price = message.text)
    await message.answer('Цена успешно сохранена!\n\nТеперь ты и все остальные могут посомтреть состав обеда с помощью команды /combo')
    combo = await state.get_data()
    # Загружаем в таблицу
    await orm_add_combo(session=session, data=combo)
    await state.clear()

# Обработчик команды /combo для просмотра комбо
@cr.message(Command('combo'))
async def viewcombo(message: Message, session: AsyncSession):
    try:
        # Получаем из таблички данные о комбо (состав[0] и цена[1])
        compound = await orm_get_combo_comp(session=session)
        if compound[0] != None:
            await message.answer(text=f'Состав обеда сегодня:\n\n{compound[0]}\n\nЦена: {compound[1]} руб')
        else:
            await message.answer('Похоже, что сегодня обеда нет или его состав пока что не ввели')
    except Exception as e:
        await message.answer('Похоже, что-то пошло не так :(\n\nОбязательно напиши об этом @NeBot100Proz')
        logger.debug(f'У {message.from_user.username} произошла ошибка при просмотре комбо: {e}')