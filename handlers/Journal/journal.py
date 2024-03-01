from aiogram import F,Router, types
from aiogram.filters import Command ,StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy.ext.asyncio import AsyncSession

from states.states import JournalState
from common.request_func import request, request_json
from database.orm_querry import  orm_get_identifiers
from handlers.Journal.JournalSupps import subject_dict, callback, semkbd, get_subject__full_info, get_subject_info

from handlers.UserSave.Encrypt import decrypt_password

from LOGGING.LoggerConfig import logger

# Journal Router
jr = Router()

@jr.message(StateFilter(None), Command('journal'))
async def journal(message: types.Message, session: AsyncSession, state: FSMContext):
    try:
        await state.set_state(JournalState.journal)
        await state.update_data(ChatID = message.chat.id)
        data =  await state.get_data()

        data = await orm_get_identifiers(session=session, id=message.chat.id)
        password = decrypt_password(key=data[2], encrypted_password=data[1])
   
    
        journal = request(username=data[0], password=password)
        courses  =journal[0]
        semesters = journal[1]
        subjects= journal[2]
        callback_list = callback(subjects)

        if len(courses) != 1:
            kbd = InlineKeyboardBuilder()
            for i in courses:
                kbd.button(text=str(i), callback_data=f'course_{i}')
            kbd.adjust(2,2,)
            await message.answer(text='Выбери курс, за который хочешь посмотреть баллы:', reply_markup=kbd.as_markup())
        else:
            if len(semesters) != 1:
                kbd = InlineKeyboardBuilder()
                
                kbd.button(text='осенний', callback_data=f'semester_осенний')
                kbd.button(text='весенний', callback_data=f'semester_весенний')
                kbd.adjust(2,)
                await message.answer('Выбери семестр, за который хочешь посмотреть баллы:', reply_markup=kbd.as_markup())
            else:
                kbd1sem = InlineKeyboardBuilder()
                for i, k in zip(subjects[0], callback_list[0]):
                    kbd1sem.button(text=i, callback_data=f'subject_{k}')
                    kbd1sem.adjust(1,)
    except:
        await message.answer('Похоже, что ты не ввел(а) логин или пароль!\n\nЧтобы посмотреть журнал нужно сначала зарегистрироваться.\n\nТыкай сюда --> /start')      
        await state.clear()
        logger.debug(f'Пользователь {message.from_user.username} решил воспользоваться командой /journal, не введя данные')

    
@jr.callback_query(StateFilter(JournalState.journal), F.data.startswith('course_'))
async def choosesem(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        kbd = InlineKeyboardBuilder()
        kbd.button(text='осенний', callback_data=f'semester_осенний')
        kbd.button(text='весенний', callback_data=f'semester_весенний')
        kbd.adjust(2,)
        await call.message.answer('Выбери семестр:', reply_markup=kbd.as_markup())
        
        await state.set_state(JournalState.Subject)
        course = call.data.split['_'][-1]
        await state.update_data(course = course)
    except:
        await call.message.answer('Похоже, что что-то пошло не так :(\n\nОбязательно напиши об этом @NeBot100Proz')
        logger.debug(f'НЕ первокурсник {call.message.from_user.username} воспользовался командой /journal и произошла ошибка после выбора курса')

@jr.callback_query(StateFilter(JournalState.Subject), F.data.startswith('semester_'))
async def lalalaal(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    try: 
        await state.update_data(semester = call.data.split('_')[-1])
        course_sem = await state.get_data()

        course = course_sem['course']
        semester = course_sem['semester']
        
        data = await orm_get_identifiers(session=session, id=call.message.chat.id)
        password = decrypt_password(key=data[2], encrypted_password=data[1])
        print(password, data[0])
        journal = request(username=data[0], password=password)

        subj_list = journal[2]

        semester_courses = {
            'осенний': {'1': 0, '2': 2, '3': 4, '4': 6},
            'весенний': {'1': 1, '2': 3, '3': 5, '4': 7}
        }

        if semester in semester_courses and course in semester_courses[semester]:
            await state.update_data(semname=semester)
            index = semester_courses[semester][course]
            subjects = subj_list[index]
            semnum = {
                '1': 'first', '2': 'second', '3': 'third', '4': 'fourth'
            }.get(course)
            kbd = semkbd(semnum=semnum, subjects=subjects)
            await call.message.answer('выбери предмет:', reply_markup=kbd)
            await state.update_data(full_list=subjects, short_list=callback(subjects=subjects))
    except:
        await call.message.answer('Похоже, что что-то пошло не так :(\n\nОбязательно напиши об этом @NeBot100Proz')
        await logger.debug(f'НЕ первокурсник {call.message.from_user.username} воспользовался командой /journal и произошла ошибка после выбора семестра')


@jr.callback_query(StateFilter(JournalState.Subject), F.data.startswith('subject_'))
async def lalalaal(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        state_data = await state.get_data()

        full = state_data['full_list']
        short = state_data['short_list']
        course = state_data['course']
        semname = state_data['semname']
        dict = subject_dict(short=short, full=full)

        subject_full = dict[f"{call.data.split('_')[-1]}"]

        
        identifiers = await orm_get_identifiers(session=session, id=call.message.chat.id)
        password = decrypt_password(key=identifiers[2], encrypted_password=identifiers[1])
        
        journal = request_json(username=identifiers[0], password=password)
        info = get_subject__full_info(course_number=course, semester_name=semname, subject_name=subject_full, journal=journal)
        
        rating = info['rating']
        exam = info['exam']
        rating_in_semester = info['rating_in_semester']
        text_rating = info['text_rating']
        control_type = info['control_type']
        medium_control_values = [item['value'] for item in info['medium_control']]

        await call.message.answer(f'Баллы за {semname} семестр по предмету <b>{subject_full}</b>:\n\nОбщие баллы в семестре: {rating_in_semester}\n\nБаллы за экзамен: {exam}\n\nРейтинг в семестре:{rating} ({text_rating})\n\nКонтрольные точки: {medium_control_values}\n\nТип контроля: <b>{control_type}</b>')
    except:
        await call.message.answer('Похоже, что что-то пошло не так :(\n\nОбязательно напиши об этом @NeBot100Proz')
        await logger.debug(f'НЕ первокурсник {call.message.from_user.username} воспользовался командой /journal и произошла ошибка после выбора предмета')


@jr.callback_query(StateFilter(JournalState.journal), F.data.startswith('semester_'))
async def сhoose_subj_for_1_course(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    
    identifiers = await orm_get_identifiers(session=session, id=call.message.chat.id)
    password = decrypt_password(key=identifiers[2], encrypted_password=identifiers[1])
    journal = request(username=identifiers[0], password=password)

    subjects= journal[2]
    callback_list = callback(subjects)
                  
    kbd1sem = InlineKeyboardBuilder()
    for i, k in zip(subjects[0], callback_list[0]):
            kbd1sem.button(text=i, callback_data=f'subject_{k}')
    kbd1sem.adjust(1,)

    kbd2sem = InlineKeyboardBuilder()
    for i, k in zip(subjects[1], callback_list[1]):
        kbd2sem.button(text=i, callback_data=f'subject_{k}')
    kbd2sem.adjust(1,)

    call_data = call.data
    semester = call_data.split('_')[-1]
    await state.update_data(sem = semester, full_list = subjects, short_list = callback_list)
    if semester == 'осенний':
        await call.answer()
        await call.message.answer('Теперь выбери предмет:', reply_markup=kbd1sem.as_markup())
    else:
        await call.answer()
        await call.message.answer('Теперь выбери предмет:', reply_markup=kbd2sem.as_markup())

    
@jr.callback_query(StateFilter(JournalState.journal), F.data.startswith('subject_'))
async def get_points_for_1_course(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):

    state_data = await state.get_data()

    full = state_data['full_list']
    short = state_data['short_list']
    semester = state_data['sem']
    result_dict = {}

    for i, k in zip(short, full):
        for h, f in zip(i,k):
            result_dict[f"{h}"] = f
    
    subject_full = result_dict[f"{call.data.split('_')[-1]}"]
    
    
    identifiers = await orm_get_identifiers(session=session, id=call.message.chat.id)
    password = decrypt_password(key=identifiers[2], encrypted_password=identifiers[1])

    journal = request_json(username=identifiers[0], password=password)
    info = get_subject_info(semester_name=state_data['sem'], subject_name=subject_full, journal=journal)
    
    rating = info['rating']
    exam = info['exam']
    rating_in_semester = info['rating_in_semester']
    text_rating = info['text_rating']
    control_type = info['control_type']
    medium_control_values = [item['value'] for item in info['medium_control']]
    
    await call.answer()
    await call.message.answer(f'Баллы за {semester} семестр по предмету <b>{subject_full}</b>:\n\nОбщие баллы в семестре: {rating_in_semester}\n\nБаллы за экзамен: {exam}\n\nРейтинг в семестре:{rating} ({text_rating})\n\nКонтрольные точки: {medium_control_values}\n\nТип контроля: <b>{control_type}</b>')