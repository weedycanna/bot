from aiogram.fsm.state import State, StatesGroup


class Newsletter(StatesGroup):
    waiting_for_content = State()
