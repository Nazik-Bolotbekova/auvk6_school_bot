from aiogram.fsm.state import State, StatesGroup

class AllStates(StatesGroup):
    request = State()
    problem = State()
    anon_not_anon = State()





