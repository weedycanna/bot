from aiogram.fsm.state import StatesGroup, State


class AddBanner(StatesGroup):
    image: str = State()