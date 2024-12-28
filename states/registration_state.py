from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    first_name = State()
    phone = State()
