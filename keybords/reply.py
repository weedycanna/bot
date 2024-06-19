from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder


start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📋 Menu'),
            KeyboardButton(text='ℹ️ About Us'),
        ],
        [
            KeyboardButton(text='💰 Payment Options'),
            KeyboardButton(text='📦 Delivery Options'),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='What are you interested in ?'
)

del_kbd = ReplyKeyboardRemove()

start_kb2 = ReplyKeyboardBuilder()
start_kb2.add(
    KeyboardButton(text='📋 Menu'),
    KeyboardButton(text='ℹ️ About Us'),
    KeyboardButton(text='💰 Payment Options'),
    KeyboardButton(text='📦 Delivery Options'),
)
start_kb2.adjust(2, 2)


start_kb3 = ReplyKeyboardBuilder()
start_kb3.attach(start_kb2)
start_kb3.row(
    KeyboardButton(text='📝 Leave feedback'),
    KeyboardButton(text='👤 Personal Info'),
)

data_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Create quiz', request_poll=KeyboardButtonPollType()),
        ],
        [
            KeyboardButton(text='Send phone number 📱', request_contact=True),
            KeyboardButton(text='Send location 🗺', request_location=True),
        ],
    ],
    resize_keyboard=True,
)
