from aiogram.fsm.state import StatesGroup, State


class Newsletter(StatesGroup):
    waiting_for_content = State()