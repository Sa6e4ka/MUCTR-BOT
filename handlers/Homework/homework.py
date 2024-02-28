import datetime
# Dd вВ
from aiogram import F, Router
from aiogram.filters import Command, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from sqlalchemy.ext.asyncio import AsyncSession

from handlers.Homework.HomeworkSupps import homework_keyboard, subject_dict
from database.orm_querry import orm_add_homework, orm_get_homework, orm_get_user_group, orm_get_identifiers
from common.request_func import request
from handlers.UserSave.Encrypt import decrypt_password

from states.states import HomeworkState
from LOGGING.LoggerConfig import logger

#Homework Router
hr = Router()

@hr.message(StateFilter(None), Command('sethomework'))
async def insert_subject(message: Message, state: FSMContext, session: AsyncSession):
    try:
        identifiers = await orm_get_identifiers(session=session, id=message.chat.id)
        password = decrypt_password(key=identifiers[2], encrypted_password=identifiers[1])
        response = request(username=identifiers[0], password=password)

        course = response[0][-1]
        current_month = datetime.datetime.now().strftime("%B")
        
        first_sem = ["September", "October", "November", "December"]
        second_sem = ["January", "February", "March", "April", "May", "June"]

        if course not in range(1, 4):
            await message.answer('Прости бро, но для магистратуры эта функция пока что недоступна\n\nЕсли хочешь пользоваться ей на постоянке, то обязательно напиши мне:\n@NeBot100Proz')
        elif current_month in first_sem:
            kbd = homework_keyboard(SubjectList=response[2][(course - 1) * 2], type='s')
            await message.answer(text='Выбери предмет, по которому хочешь загрузить домашку', reply_markup=kbd)
        elif current_month in second_sem:
            kbd = homework_keyboard(SubjectList=response[2][(course - 1) * 2 + 1], type='s')
            await message.answer(text='Выбери предмет, по которому хочешь загрузить домашку', reply_markup=kbd)
        else:
            await message.answer('Бро, учеба еще не началась, какая домашка?')
        await state.set_state(HomeworkState.subject)
        await state.update_data(chat_id = message.chat.id)
    except TimeoutError:
        await message.answer('Что-то ты слишком долго думаешь...\n\nЕсли все-таки надумал(а), то воспользуйся командой еще раз!')
        logger.debug(f'Пользователь {message.from_user.username} слишом долго думал при выборе предмета для загрузки домашки')
    except Exception:
        await message.answer('Похоже, что ты не ввел(а) логин или пароль!\n\nЧтобы загрузить домашку, нужно сначала зарегистрироваться\n\nТыкай сюда --> /start')
        logger.debug(f'Пользователь {message.from_user.username} воспользовался /sethomework, не введя данные')


@hr.callback_query(StateFilter(HomeworkState.subject), F.data.startswith('s_'))
async def sethomework(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()

    identifiers = await orm_get_identifiers(session=session, id=call.message.chat.id)
    password = decrypt_password(key=identifiers[2], encrypted_password=identifiers[1])
    response = request(username=identifiers[0], password=password)

    SubjectList = response[2]
    dict = subject_dict(full=SubjectList)
    
    if call.message.chat.id == state_data['chat_id']:
        try:
            subject = call.data.split("_")[1]
            await state.update_data(subject=dict[subject])
            await call.message.answer(
                f'Ты выбрал предет {dict[subject]}\nТеперь введи домашнее задание:'
            )
            await state.set_state(HomeworkState.task)
        except Exception:
            logger.info(f'Пользователю {call.message.from_user.username} выдало ошибку во время ввода дз (функция sethomework)')
            await call.message.answer('Похоже, что возникла какая-то ошибка :(\n\nОбязательно обратись к @Nebot100proz')
    else:
        logger.info(f'Пользователю {call.message.from_user.username} выдало ошибку во время ввода дз из-за несоответствия chat id')
        await call.message.answer('Боюсь, что кто-то другой начал вводить домашнее задание раньше тебя :(\n\nПопробуй чуть позже /sethomework')
        await state.clear()


@hr.message(StateFilter(HomeworkState.task), or_f(F.text, F.photo, F.audio, F.voice, F.video, F.document, F.sticker))
async def task(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()

    if message.chat.id == state_data['chat_id']:
        group = await orm_get_user_group(session=session, id=message.chat.id)
        if message.text:
            await state.update_data(task = message.text, group=group, Ctype = 'text', caption= '')
            HW_data = await state.get_data()
            await orm_add_homework(session=session, data=HW_data)
            await message.answer(f'Домашнее задание по предмету <b>{state_data['subject']}</b> успешно сохранено!\n\nПосмотреть его можно по команде /viewhomework!')
            await state.clear()
        elif message.voice:
            await state.update_data(task = message.voice.file_id, group=group, Ctype = 'voice', caption= '')
            HW_data = await state.get_data()
            await orm_add_homework(session=session, data=HW_data)
            await message.answer(f'Домашнее задание по предмету <b>{state_data['subject']}</b> успешно сохранено!\n\nПосмотреть его можно по команде /viewhomework!')
            await state.clear()
        elif message.audio:
            await state.update_data(task = message.audio.file_id, group=group, Ctype = 'audio', caption= '')
            HW_data = await state.get_data()
            await orm_add_homework(session=session, data=HW_data)
            await message.answer(f'Домашнее задание по предмету <b>{state_data['subject']}</b> успешно сохранено!\n\nПосмотреть его можно по команде /viewhomework!')
            await state.clear()
        elif message.sticker:
            await state.update_data(task = message.sticker.file_id, group=group, Ctype = 'sticker', caption= '')
            HW_data = await state.get_data()
            await orm_add_homework(session=session, data=HW_data)
            await message.answer(f'Домашнее задание по предмету <b>{state_data['subject']}</b> успешно сохранено!\n\nПосмотреть его можно по команде /viewhomework!')
            await state.clear()
        elif message.photo:
            await state.update_data(task = message.photo[-1].file_id, group=group, Ctype = 'photo')
            await message.answer(f'<b>Теперь введи описание к фото\n\nЕсли не нужно описание - введи /empty</b>')
            await state.set_state(HomeworkState.caption)
        elif message.video:
            await state.update_data(task = message.video.file_id, group=group, Ctype = 'video')
            await message.answer(f'<b>Теперь введи описание к видео\n\nЕсли не нужно описание - введи /empty</b>')
            await state.set_state(HomeworkState.caption)
        elif message.document:
            await state.update_data(task = message.document.file_id, group=group, Ctype = 'document')
            await message.answer(f'<b>Теперь введи описание к документу\n\nЕсли не нужно описание - введи /empty</b>')
            await state.set_state(HomeworkState.caption)
    else:
        logger.info(f'Пользователю {message.from_user.username} выдало ошибку во время ввода дз из-за несоответствия chat id')
        await message.answer('Боюсь, что кто-то другой начал вводить домашнее задание раньше тебя :(\n\nПопробуй чуть позже /sethomework')
        await state.clear()

@hr.message(HomeworkState.caption, Command('empty'))
async def empty(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    if message.chat.id == state_data['chat_id']:
        try:
            await state.update_data(caption = '')
            HW_data = await state.get_data()
            await orm_add_homework(session=session, data=HW_data)
            await message.answer(f'Домашнее задание по предмету <b>{HW_data['subject']}</b> успешно сохранено!\n\nПосмотреть его можно по команде /viewhomework!')
            await state.clear()
        except TimeoutError:
            logger.debug(f'Пользователь {message.from_user.username} слишком долго не вводил домашнее задание')
            await message.answer('Что-то ты слишком долго думаешь...\n\nЕсли все-таки надумал(а), то воспользуйся командой еще раз!')
            await state.clear()
    else:
        logger.info(f'Пользователю {message.from_user.username} выдало ошибку во время ввода дз из-за несоответствия chat id')
        await message.answer('Боюсь, что кто-то другой начал вводить домашнее задание раньше тебя :(\n\nПопробуй чуть позже /sethomework')
        await state.clear()

       
@hr.message(HomeworkState.caption, F.text)
async def caption_func(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    if message.chat.id == state_data['chat_id']:
        try:
            await state.update_data(caption=message.text)
            HW_data = await state.get_data()
            await orm_add_homework(session=session, data=HW_data)
            await message.answer(f'Домашнее задание по предмету <b>{HW_data['subject']}</b> успешно загружено!\n\nПосмотреть его можно по команде /viewhomework!')
            await state.clear()
        except TimeoutError:
            logger.debug(f'Пользователь {message.from_user.username} слишком долго не вводил домашнее задание')
            await message.answer('Что-то ты слишком долго думаешь...\n\nЕсли все-таки надумал(а), то воспользуйся командой еще раз!')
            await state.clear()
    else:
        logger.info(f'Пользователю {message.from_user.username} выдало ошибку во время ввода дз из-за несоответствия chat id')
        await message.answer('Боюсь, что кто-то другой начал вводить домашнее задание раньше тебя :(\n\nПопробуй чуть позже /sethomework')
        await state.clear()


@hr.message(StateFilter(None),Command('viewhomework'))
async def choose_viewhomework(message: Message, session: AsyncSession):
    try:
        identifiers = await orm_get_identifiers(session=session, id=message.chat.id)
        password = decrypt_password(key=identifiers[2], encrypted_password=identifiers[1])
        response = request(username=identifiers[0], password=password)

        course = response[0][-1]
        current_month = datetime.datetime.now().strftime("%B")

        first_sem = ["September", "October", "November", "December"]
        second_sem = ["January", "February", "March", "April", "May", "June"]

        if course not in range(1, 5):
            await message.answer('Прости бро, но для магистратуры эта функция пока что недоступна, потому что в этом нет нужды.\n\nЕсли хочешь пользоваться ей на постоянке, то обязательно напиши мне:\n@NeBot100Proz')
        elif current_month in first_sem:
            kbd = homework_keyboard(SubjectList=response[2][(course - 1) * 2], type='v')
            await message.answer(text='Выбери предмет, по которому хочешь посмотреть домашку', reply_markup=kbd)
        elif current_month in second_sem:
            kbd = homework_keyboard(SubjectList=response[2][(course - 1) * 2 + 1], type='v')
            await message.answer(text='Выбери предмет, по которому хочешь посмотреть домашку', reply_markup=kbd)
        else:
            await message.answer('Бро, учеба еще не началась, какая домашка?')
    except TimeoutError:
        await message.answer('Что-то ты слишком долго думаешь...\n\nЕсли все-таки надумал(а), то воспользуйся командой еще раз!')
        logger.debug(f'Пользователь {message.from_user.username} слишом долго думал при выборе предмета для просмотра домашки')
    except Exception as e:
        await message.answer('Похоже, что ты не ввел(а) логин или пароль!\n\nЧтобы посмотреть домашку нужно сначала зарегистрироваться\n\nТыкай сюда --> /start\n\nЕсли не получится после регистрации, то напиши @NeBot100Proz')
        logger.debug(f'Пользователь {message.from_user.username} воспользовался /viewhomework, не введя данные')

@hr.callback_query(F.data.startswith('v_'))
async def viewhomework(call: CallbackQuery, session: AsyncSession):
    
    response_methods = {
            'text': call.message.answer,
            'voice': call.message.answer_voice,
            'photo': call.message.answer_photo,
            'audio': call.message.answer_audio,
            'video': call.message.answer_video,
            'document': call.message.answer_document,
            'sticker': call.message.answer_sticker,
        }

    identifiers = await orm_get_identifiers(session=session, id=call.message.chat.id)
    password = decrypt_password(key=identifiers[2], encrypted_password=identifiers[1])
    response = request(username=identifiers[0], password=password)

    SubjectList = response[2]
    dict = subject_dict(full=SubjectList)

    try:
        call_data = call.data.split('_')[1]
        group = await orm_get_user_group(session=session, id=call.message.chat.id)
        homework = await orm_get_homework(session= session, subject= dict[call_data], group=group)
        task = homework[0]
        ctype = homework[1]
        caption = homework[2]
        response_method = response_methods.get(ctype)
        if ctype == 'text':
            await call.answer()
            await call.message.answer(text=f'Последнее домашнее задание по предмету\n<b>{dict[call_data]}</b>\n\n{task}')
        elif ctype == 'audio':
            await call.answer()
            await response_method(caption = f'Последнее домашнее задание по предмету\n<b>{dict[call_data]}</b>', **{ctype:task})
        elif ctype == 'voice':
            await call.answer()
            await response_method(caption = f'Последнее домашнее задание по предмету\n<b>{dict[call_data]}</b>', **{ctype:task})
        else:
            if caption != '':
                await call.answer()
                await response_method(caption=f'Последнее домашнее задание по предмету\n<b>{dict[call_data]}</b>\n\n<b>Описание:</b>\n\n{caption}', **{ctype:task})
            else:
                await call.answer()
                await response_method(caption=f'Последнее домашнее задание по предмету\n<b>{dict[call_data]}</b>', **{ctype:task})
    except Exception as e:
        await call.message.answer('Похоже, что задание по этому предмету еще не добавили :(\n\nБудь первым! --> /sethomework')
    