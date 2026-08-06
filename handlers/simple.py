from aiogram import F, Bot, Router, types
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

from kbds import inline
from common.schedule import *
from LOGGING.LoggerConfig import logger

from database.orm_querry import orm_get_user_group
from states.states import MapState


sr = Router()

#simple router
# Обработчик команды /map
@sr.message(StateFilter(None, MapState), Command('map'))
async def choose_floor_miusi(message: types.Message, state: FSMContext):
    await message.answer(text='Выбери корпус, карту которого хотел(а) бы посмотреть',reply_markup=inline.korpus_mapKB.as_markup())
    await state.set_state(MapState.Choose)


# Если пользователь выбрал посмотреть карту Миус
@sr.callback_query(StateFilter(MapState.Choose), F.data == 'Miusi')
async def show_floor_miusi(call: types.CallbackQuery, state : FSMContext):
    await call.message.edit_text('Выбери этаж Миусского корпуса', reply_markup=inline.Miusi_mapKB.as_markup())
    await state.set_state(MapState.Miusi)
    await state.clear()


@sr.callback_query(F.data.startswith('M_'))
async def show_floor_miusi(call: types.CallbackQuery, bot: Bot, state : FSMContext):
    data = call.data.split('_')[1]
    floor_list = ['1 этаж', '2 этаж','3 этаж','4 этаж','5 этаж']
    url_list = [
        'https://sun9-40.userapi.com/impg/fuq9c7BJNIIUdIYlcn1lF4vyVXT_pizt_MWyTQ/AOoJtwgHHc8.jpg?size=604x435&quality=96&sign=dfa0a79b78c2203d945403c3c007a123&c_uniq_tag=zsP2sdQNAV9jwj_ggy3N9r-XaU0MCZ8pt6SKrTMgkr0&type=album',
        'https://sun9-28.userapi.com/impg/SVv_PqKcQGjKrjHYO1wdifAKAL5dWZypQiow8Q/1h0s8DitpQs.jpg?size=604x412&quality=96&sign=30a9c17830fc685be6c7b777822100a6&type=album',
        'https://sun9-35.userapi.com/impg/bluq_qNROfR8rFuEKDhetgXvfntKVh2TAraGtQ/cQpnFLh7t-I.jpg?size=604x402&quality=96&sign=315e1a3ae9390fea66631cfd720a9226&c_uniq_tag=RKYQEJDq9yKMXjZMPx2UrBg3ByRbsQv7JHI8l0hF8P8&type=album',
        'https://sun9-37.userapi.com/impg/M5LkULGzb75bh5fGs8Cuiqdq6d_kNqS5U1oVag/CBkBYcnMANE.jpg?size=604x404&quality=96&sign=4ea417e6bc0434c1c2e2b10915294adf&c_uniq_tag=lnsYPOpH7VzZGjPSXW0wmOuvyMHaLFmGiaiDRc6265w&type=album',
        'https://sun9-34.userapi.com/impg/rA6h4UyMaNriNdScQHqqN_pUTRR2R2aX8LHWfw/vbPooT0qcpo.jpg?size=604x434&quality=96&sign=5aac2040d90a4c657435572bed21e29f&c_uniq_tag=lRJkFd4-2z7oB0g-FkJA0dlm1qsgnAcGPyyDuzFsfaA&type=album'    
    ]
    if data == floor_list[0]:
        await call.message.answer_photo(photo= url_list[0], caption='Карта первого этажа:')
    elif data == floor_list[1]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[1], caption='Карта второго этажа:')
    elif data == floor_list[2]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[2], caption='Карта третьего этажа:')
    elif data == floor_list[3]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[3], caption='Карта четвертого этажа:')
    elif data == floor_list[4]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[4], caption='Карта пятого этажа:')


# Если пользователь выбрал посмотреть карту Тушки
@sr.callback_query(StateFilter(MapState.Choose), F.data == 'Tushka')
async def show_floor_miusi(call: types.CallbackQuery, state : FSMContext):
    await call.message.edit_text('Выбери этаж Тушинского корпуса', reply_markup=inline.Tushka_mapKB.as_markup())

    await state.set_state(MapState.Tushka)
    await state.clear()

@sr.callback_query(F.data.startswith('T_'))
async def show_floor_miusi(call: types.CallbackQuery, bot: Bot):
    data = call.data.split('_')[1]
    floor_list = ['1 этаж', '2 этаж','3 этаж','4 этаж','5 этаж','6 этаж','7 этаж','8 этаж','9 этаж']
    url_list = [
        'https://sun1-56.userapi.com/impg/Fm1CswDj95h5n__7GEbngVjiD-k_kvRaAvs2zA/O1yeNUA0Bo0.jpg?size=604x587&quality=96&sign=6ca15074d424c8c6f312b40fa3e4a928&type=album',
        'https://sun1-85.userapi.com/impg/TGBCUAiaqfWRR4g3HTPTEzK_uvasObcjIIDUDw/QJsZFc1Y5Ao.jpg?size=571x604&quality=96&sign=dbe7bbc171b51568fcdee57ee8147759&type=album',
        'https://sun1-27.userapi.com/impg/c857428/v857428299/16e700/upzUKLa9MFw.jpg?size=604x518&quality=96&sign=27d4eb3a7b3552c6574cab845c28be93&type=album',
        'https://sun9-49.userapi.com/impg/c855128/v855128299/1df90b/T4JiJCBkuYw.jpg?size=604x383&quality=96&sign=6881452994b7b669767a8de9ef5149e2&type=album',
        'https://sun1-96.userapi.com/impg/c857036/v857036299/681e9/U3yURirW7Yg.jpg?size=604x345&quality=96&sign=104d3bcb63eeb1624b60dcef226ae396&type=album',
        'https://sun9-69.userapi.com/impg/c853520/v853520299/1e7508/vL9V2uXWeoE.jpg?size=604x339&quality=96&sign=e33eac0cedb46e6898076361493b069f&type=album',
        'https://sun1-20.userapi.com/impg/lNMAPKPRIw9CU0CC_vABdj6-V_QUpRIlFpIxrg/o-TharUXE7o.jpg?size=604x326&quality=96&sign=1e53f7904cc7946bdbbed9df0bda76e1&type=album',
        'https://sun1-98.userapi.com/impg/v19zs03bnrlE5H_rBdzsDIrHd97lhx4J2xENuw/QUxkQDktk_I.jpg?size=604x331&quality=96&sign=fa3a48db3b7b22bb5a1d58b7a5deead4&type=album',
        'https://sun1-88.userapi.com/impg/1yYgKxPV5oYtAGGzHNUegLQv0ADh0l2nYl6hiw/o00tgrrbbjQ.jpg?size=604x333&quality=96&sign=b606c9e8a17c17f630d81a9f7b486759&type=album'   
    ]
    if data == floor_list[0]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[0], caption='Карта первого этажа:')
    elif data == floor_list[1]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[1], caption='Карта второго этажа:')
    elif data == floor_list[2]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[2], caption='Карта третьего этажа:')
    elif data == floor_list[3]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[3], caption='Карта четвертого этажа:')
    elif data == floor_list[4]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[4], caption='Карта пятого этажа:')
    elif data == floor_list[5]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[5], caption='Карта шестого этажа:')
    elif data == floor_list[6]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[6], caption='Карта седьмого этажа:')
    elif data == floor_list[7]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[7], caption='Карта восьмого этажа:')
    elif data == floor_list[8]:
        await call.bot.send_photo(call.message.chat.id, photo= url_list[8], caption='Карта девятого этажа:')


@sr.message(Command('schedule'))
async def schedule(message: types.Message, session: AsyncSession):
    try:
        group = await orm_get_user_group(session=session, id=message.chat.id)
    
        if group == '856':
            current_day = datetime.datetime.today().weekday()
            if current_day == 0:
                await message.answer(text=f'Расписание на сегодня:\n\n{Monday}')
            elif current_day == 1:
                await message.answer(text= f'Расписание на сегодня:\n\n{Tuesday}')
            elif current_day == 2:
                await message.answer(text= f'Расписание на сегодня:\n\n{Wednesday}')
            elif current_day == 3:
                await message.answer(text=f'Расписание на сегодня:\n\n{Thursday}')
            elif current_day == 4:
                await message.answer(text= f'Расписание на сегодня:\n\n{Friday}')
            elif current_day == 5:
                await message.answer(text= f'Расписание на сегодня:\n\n{Saturday}')
            elif current_day == 6:
                await message.answer(text= f'Расписание на сегодня:\n\n{Sunday}')
        else:
            logger.info(f'Пользователь {message.from_user.username} из группы {group} решил посмотреть расписание')
            await message.answer('Эта функция пока что в разработке 🥴\n\nУже совсем скоро ты сможешь ею пользоваться!')
    except: 
        logger.debug(f'Пользователь {message.from_user.username} воспользовался /schedule, не введя данные')
        await message.answer('Эта функция пока что в разработке 🥴\n\nУже совсем скоро ты сможешь ею пользоваться!')



