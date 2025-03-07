from aiogram.fsm.state import State, StatesGroup


class StepGetPhysicsFormul(StatesGroup):

    '''Класс для машины состояния при вводе физических формул'''

    GET_FORMULS = State()


class StepAppendPhysicsFormuls(StatesGroup):

    '''Класс для машины состояния при добавление админом формулы в базу данных'''

    VALUE = State()
    DESCRIPTION = State()
    FORMUL = State()
    DESCRIPTION_FORMUL = State()
    UNIT = State()
    CHAPTER = State()

    ACCEPT = State()
