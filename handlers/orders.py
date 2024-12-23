from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup, InputMediaPhoto
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Order, Cart
from keybords.inline import MenuCallBack, get_user_main_btns, get_back_button
from queries.banner_queries import orm_get_banner
from queries.order_queries import orm_get_user_orders
from states.order_state import OrderState
from aiogram import F, Router, types
from aiogram.filters import Command

from typing import Union
from aiogram.types import CallbackQuery, Message

from utils.utils import format_phone_number

order_router = Router()


@order_router.callback_query(MenuCallBack.filter(F.menu_name == "order"))
async def start_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please enter your name:")
    await state.set_state(OrderState.name)
    await callback.answer()


@order_router.message(OrderState.name, F.text)
async def process_name(message: types.Message, state: FSMContext):
    if len(message.text) < 2 or len(message.text) > 50:
        await message.answer("Name must be between 2 and 50 characters. Please enter your name again:")
        return
    await state.update_data(name=message.text)
    await message.answer("Please enter your phone number:", reply_markup=get_back_button())
    await state.set_state(OrderState.phone)


@order_router.message(OrderState.phone, F.text)
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Back":
        await message.answer("Please enter your name again:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(OrderState.name)
        return

    formatted_phone = format_phone_number(message.text)
    if not formatted_phone:
        await message.answer("Invalid phone number. Please enter a valid phone number (10-15 digits):")
        return

    await state.update_data(phone=formatted_phone)
    await message.answer("Phone number accepted. Please enter your address:", reply_markup=get_back_button())
    await state.set_state(OrderState.address)


@order_router.message(OrderState.address, F.text)
async def process_address(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Back":
        await message.answer("Please enter your phone number again:", reply_markup=get_back_button())
        await state.set_state(OrderState.phone)
        return

    if len(message.text) < 5 or len(message.text) > 100:
        await message.answer("Address must be between 5 and 100 characters. Please enter your address again:")
        return

    await state.update_data(address=message.text)
    user_data = await state.get_data()

    confirmation_message = (
        f"Please confirm your order details:\n\n"
        f"Name: {user_data['name']}\n"
        f"Phone: {user_data['phone']}\n"
        f"Address: {user_data['address']}\n\n"
        "Is everything correct?"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Confirm ✅", callback_data="confirm_order"),
                InlineKeyboardButton(text="Cancel ❌", callback_data="cancel_order")
            ]
        ]
    )

    await message.answer(confirmation_message, reply_markup=keyboard)
    await state.set_state(OrderState.confirm)


@order_router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    current_state = await state.get_state()

    if current_state is None:
        await callback.answer("This order has already been processed!", show_alert=True)
        return

    try:
        user_data = await state.get_data()

        new_order = Order(
            user_id=callback.from_user.id,
            name=user_data.get('name', ''),
            address=user_data.get('address', ''),
            phone=user_data.get('phone', ''),
            status="pending"
        )

        session.add(new_order)
        await session.commit()

        await session.execute(
            delete(Cart).where(Cart.user_id == callback.from_user.id)
        )
        await session.commit()

        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            "Your order has been confirmed! ✅",
            reply_markup=get_user_main_btns(level=1)
        )

        await state.clear()
        await callback.answer("Order successfully created!", show_alert=True)

    except Exception as e:
        await session.rollback()
        await callback.answer("Error creating order. Please try again.", show_alert=True)
        return


@order_router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer("This order has already been processed!", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

    await callback.message.answer("Order canceled ❌", reply_markup=ReplyKeyboardRemove())

    await state.clear()


@order_router.callback_query(F.data.startswith("edit_"))
async def handle_edit(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[1]
    if field == "name":
        await callback.message.answer("Please enter your name again:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(OrderState.name)
    elif field == "phone":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⬅️ Back")],
            ],
            resize_keyboard=True
        )
        await callback.message.answer("Please enter your phone number again:", reply_markup=keyboard)
        await state.set_state(OrderState.phone)
    elif field == "address":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⬅️ Back")],
            ],
            resize_keyboard=True
        )
        await callback.message.answer("Please enter your address again:", reply_markup=keyboard)
        await state.set_state(OrderState.address)

    await callback.answer()


@order_router.message(Command("orders"))
@order_router.callback_query(MenuCallBack.filter(F.menu_name == "orders"))
async def process_orders_command(update: Union[CallbackQuery, Message], session: AsyncSession):
    try:
        if isinstance(update, CallbackQuery):
            user_id = update.from_user.id
            target = update.message
            is_callback = True
        else:
            user_id = update.from_user.id
            target = update
            is_callback = False

        orders = await orm_get_user_orders(session, user_id)

        if not orders:
            text = "У вас пока нет заказов."
        else:
            text = ""
            for order in orders:
                text += (
                    f"🔸 Заказ {order.id}\n"
                    f"👤 Имя: {order.name}\n"
                    f"📦 Статус: {order.status}\n"
                    f"📍 Адрес: {order.address}\n"
                    f"📱 Телефон: {order.phone}\n"
                    f"-------------------\n"
                )

        banner = await orm_get_banner(session, "orders")

        media = InputMediaPhoto(
            media=banner.image,
            caption=f"<strong>{banner.description}</strong>\n\n{text}"
        )

        if is_callback:
            await target.edit_media(
                media=media,
                reply_markup=get_user_main_btns(level=1)
            )
            await update.answer()
        else:
            await target.answer_photo(
                photo=banner.image,
                caption=f"<strong>{banner.description}</strong>\n\n{text}",
                reply_markup=get_user_main_btns(level=1),
                parse_mode="HTML"
            )

    except Exception as e:
        if is_callback:
            await update.answer("Произошла ошибка при получении заказов", show_alert=True)
        else:
            await update.answer("Произошла ошибка при получении заказов")