from aiogram.fsm.state import State, StatesGroup

# Состояние для загрузки комбо-обеда
class СomboState(StatesGroup):
    compound = State()
    price = State()

# Состояние для загрузки домашнего задания
class HomeworkState(StatesGroup):
    subject = State()
    task = State()

# Состояние для просмотра журнала
class JournalState(StatesGroup):
    journal = State()
    Subject = State()

# Состояние для просмотра карты
class MapState(StatesGroup):
    Choose = State()
    Miusi = State()
    Tushka = State()

# Состояние регистрации
class SignUpState(StatesGroup):
    Agreement = State()
    Identify = State()
    login = State()
    password = State()

# Состояние отправки новости 

class AnnounceState(StatesGroup):
    announcement = State()

StateTouple = (СomboState.compound ,СomboState.price, HomeworkState.subject ,HomeworkState.task, JournalState, MapState, SignUpState, AnnounceState)      