#Импортируем нужные дополнительные модули
import os
import asyncio
from LOGGING.LoggerConfig import logger

# Импортируем нужные модули из aiogram
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command ,StateFilter
from aiogram.types import BotCommandScopeAllPrivateChats, Message, BufferedInputFile 
from aiogram.fsm.context import FSMContext

#Достаем токен бота и url базы данных из переменной окружения
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

# Имопртируем функцию создания базы данных
try:
    from database.engine import create_db, drop_db,  session_maker
except Exception as e:
    logger.error(f'Ошибка в запросе к sql: {e}')

#Из папки handlers импортируем все хендлеры 
from handlers.Combo import cr
from handlers.Admin import ar
from handlers.Journal.Journal import jr
from handlers.Homework.Homework import hr
from handlers.Simple import sr
from handlers.UserSave.UserSave import ur
from handlers.ExceptionHandler import er
# Из папки common импортируем команды
from common.commands import private


#Создаем объект бота (передаем ему режим парсига получаемых ответов)
bot= Bot(token=os.getenv('TOKEN'), default=ParseMode.HTML)
#Создаем объект диспетчера
dp = Dispatcher()

# Добавляем Middlewares 
    # Чтобы использовать не одно конкретное событие, а любое можно заменить message на update
from middlewares.db import DataBaseSession

#Подключаем к диспетчеру все роутеры из содаваемых хендлеров. 
dp.include_routers(jr ,sr, cr, hr,ar, ur, er) 


# Добавляем основные "глобальные" хендлеры
@dp.message(Command('state'))
async def state_get(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(
        text=f'Текущее состояние: {current_state}'
    )

# Команда очистки состояния
@dp.message(Command('stateclear'))
async def clear_state(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await state.clear()
    clear_state = await state.get_state()
    await message.answer(f'Состояние <b>{current_state}</b> сменилось на <b>{clear_state}</b>')


# Команда получения логов
@dp.message(Command('loggs'))
async def sendloggs(message: Message):
        fp = ['LOGGING/DEBUG.txt','LOGGING/ERROR.txt']
        for f in fp:
            try:
                file = BufferedInputFile.from_file(path=f)
                await message.answer_document(document=file)
            except Exception:
                name = f.split('/')[-1]
                await message.answer(f'Файл <b>{name}</b> пуст')
        
# Команда экстренной очистки базы данных
@dp.message(Command('DROPDATABASE'))
async def drop(message: Message):
    await drop_db()
    await message.answer('База данных полностью очищена')


#Запускаем бота, помещаем доступные апдейты в start_polling
# отключаем обработку незавершившихся запросов
# Подключаем базу данных
async def main():
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await create_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private,scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot,allowed_updates=dp.resolve_used_update_types())
    

# Запуск main
if __name__ == "__main__":
    try:   
        print("I'M ALIVE BIIIYYYAAAATCH")
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен!')
        pass
    except Exception as e:  
        logger.error(f'КРИТИЧЕСКАЯ ОШИБКА: {e}')