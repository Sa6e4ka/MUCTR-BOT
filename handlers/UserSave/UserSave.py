from aiogram import F, Bot, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from LOGGING.LoggerConfig import logger

from database.orm_querry import orm_add_user, orm_get_user_group, orm_get_group_users_list, orm_get_users_ids
from common.request_func import request

from handlers.UserSave.Encrypt import generate_key, encrypt_password

from states.states import SignUpState, AnnounceState
from kbds.inline import AuthKB

#User Router
ur = Router()

""" 
✡ Обработчики ввода данных :

    √ Сначала выдаем пользователю соглашение об обработке персональных данных
        Если он согласен, то начинаем регистрацию

    √ Получаем айдишники всех юзеров
    √ Создаем ключ шифрования и шифруем введенный пароль
    
    √ Обновление данных пользователя, если его чат айди уже есть в базе:
        ☀ Получаем группу пользователя, отправляя запрос на eios
        ☀ Опять получаем всю дату словарика состояния 
        ☀ Загружаем все данные пользователя в базу 
        ☀ Логируем если пользователь успешно обновил данные (и если неуспешно, тоже)
    √Если пользователь неправильно вводит данные, то не срабатывет функция для получения группы
        ☀ Добавление нового пользователя (все то же самое, описывать еще раз нет смысла)
        ☀ Логируем если пользователь успешно ввел данные (и если неуспешно, тоже)

"""

# Обработчик команды /start
@ur.message(StateFilter(None), CommandStart())
async def start(message: Message):  
    logger.info(f'Новый пользователь: {message.from_user.username}')
    await message.answer('Немного формальностей 🙄\n\nСейчас тебе нужно будет ввести логин и пароль от EIOS.\n\n<b>Однако есть небольшие проблемки в их хранении 😅</b>\n\nСкажи, ты согласена(на) с условиями конфиденциальности, написанными на <a href="https://sites.google.com/view/muctr-helper/%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F-%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0">сайте бота</a>?', reply_markup=AuthKB.as_markup())


#Пользователь согласен
@ur.callback_query(F.data == 'Согласен(на)')
async def agree(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Отлично!\n\n<b>Тогда введи логин от портала EIOS:</b>')
    await state.set_state(SignUpState.Identify)


#Пользователь не согласен
@ur.callback_query(F.data == 'Не согласен(на)')
async def not_agree(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer() 
    await call.message.answer('Очень жаль 😢\n\nВ таком случае тебе будет доступен не весь функционал бота.\n\nПочему? Можешь прочитать об этом на <a href="https://sites.google.com/view/muctr-helper/%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F-%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0">сайте</a>\n\nТы можешь использовать только команды /map, /menu и /setmenu')


# Просьба ввести пароль
@ur.message(StateFilter(SignUpState.Identify), F.text)
async def SaveLog(message: Message, state: FSMContext):
    if len(message.text) == 6 and message.text.isdigit():
        await state.update_data(username = message.from_user.username, 
                                chat_id = message.chat.id,
                                login = message.text)    
        await message.answer(text='Спасибо!\n\n<b>Теперь введи пароль:</b>')
        await state.set_state(SignUpState.password)
    else:
        await state.clear()
        await message.answer(f'{message.from_user.username}<b>, пожалуйста, введи логин правильно!</b>')
        await state.set_state(SignUpState.Identify)
        await state.update_data(username = message.from_user.username, 
                                chat_id = message.chat.id,
                                login = message.text)   


# Добавление пользователя в базу данных
@ur.message(StateFilter(SignUpState.password), F.text)
async def SavPas(message: Message, state: FSMContext, session: AsyncSession):
    key = generate_key()
    encrypted_password = encrypt_password(password=message.text, key=key)
    try:
        data = await state.get_data()
        response = request(username=data['login'], password=message.text)
        group = response[3]
        await state.update_data(group = group, password = encrypted_password, key=key)
        f_data = await state.get_data()
        await orm_add_user(session=session,data=f_data)
        await message.answer('Твой логин успешно сохранен, а пароль даже зашифрован 🤓')
        await state.clear()
        await asyncio.sleep(1)
        await message.answer('<b>НЕБОЛЬШОЙ МАНУАЛЬЧИК</b>\n\nТеперь ты можешь загрузить домашку для своих одногруппников\n👉🏿 /sethomework\n\nEсли кто-то другой загрузил ее раньше тебя, ты уже можешь ее посмотреть\n👉🏿 /viewhomework\n\nЧто бы посмотреть баллы из журнала EIOS тыкай сюда\n👉🏿 /journal\n\n<b>Остальные функции смотри в менюшке слева</b>')
    except Exception as e:
        logger.debug(f'Пользователь {message.from_user.username} неправильно ввел данные: {e}')
        await message.answer('Похоже, что ты ввел(а) неверные логин или пароль😭\n\nПопробуй еще раз --> /start')
        await state.clear()
            
"""

✡ Добавление новости:

    √ Получаем группу пользователя по его чат ай ди
    √ По его группе получаем список его одногруппников
    √ Делаем проверку на тип контента 
    √ Обрабатываем ошибку слишком долгого ожидания

"""

# Обработчик команды /an для ввода новости
@ur.message(StateFilter(None), Command('an'))
async def an(message: Message, state: FSMContext):
    await message.answer(text='Введи новость:')
    await state.set_state(AnnounceState.announcement)


@ur.message(StateFilter(AnnounceState.announcement), or_f(F.text, F.photo, F.audio, F.voice, F.video, F.document))
async def add_news(message: Message, session: AsyncSession, state: FSMContext, bot : Bot):
    try:
        id = message.chat.id
        group = await orm_get_user_group(session=session, id=id)
        group_users_list = await orm_get_group_users_list(session=session, group=group)
        await message.answer(text=f'<b>Новость полетела одногруппникам!👇🏿</b>')
        
    
        content_mapping = {'message.audio': 'message.audio.file_id',
                           'message.photo': 'message.photo[-1].file_id', 
                           'message.video': 'message.video.file_id',
                           'message.voice': 'message.voice.file_id',
                           'message.document': 'message.document.file_id',
                            'message.sticker' : 'message.sticker.file_id'}   
        content = content_mapping.keys()
        for user_id in group_users_list:
            if not message.text:
                for i in content:
                    if eval(i):
                        send_methot =getattr(bot, f'send_{i.split('.')[-1]}')
                        await send_methot(user_id, eval(content_mapping[i]), caption=f'<code>Новость от старосты</code>')  
                        await state.clear()
                        break
            else:
                await bot.send_message(user_id, f'<code>Новость от старосты:</code>\n\n{message.text}')
                await state.clear()
    except TimeoutError:
        logger.debug(f'Староста ({message.from_user.username}) слишком долго не загружала новость')
        await message.answer('Что-то долго ты думаешь, староста...')
        await state.clear()
    except Exception as e:
        await state.clear()
        await message.answer('<b>Что-то пошло не так 😭</b>\n\nПохоже ты не зарегистрировался(лась)')
        logger.debug(f'Ошибка у старосты {message.from_user.username} при попытке отправить новость\n{e} ')
        

       