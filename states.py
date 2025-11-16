from aiogram.fsm.state import State, StatesGroup

class AllStates(StatesGroup):
    request = State()
    problem = State()                # все фсм состояния
    anon_not_anon = State()
    full_name_and_grade = State()
    сonfirm_cancel = State()






