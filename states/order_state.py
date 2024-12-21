from aiogram.fsm.state import StatesGroup, State


class OrderState(StatesGroup):
    name = State()
    phone = State()
    address = State()
    confirm = State()
