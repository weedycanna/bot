from aiogram.fsm.state import State, StatesGroup


class AddBanner(StatesGroup):
    image = State()
