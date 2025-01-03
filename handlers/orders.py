import os
from typing import Union

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from django.conf import settings

from callbacks.callbacks import OrderDetailCallBack
from filters.chat_types import ChatTypeFilter
from keybords.inline import MenuCallBack, get_order_details_keyboard, get_user_main_btns
from keybords.reply import get_back_button
from queries.banner_queries import get_banner
from queries.cart_queries import clear_cart, get_cart_items
from queries.order_queries import (
    add_order_with_items,
    get_order_by_id,
    get_order_items,
    get_user_orders,
)
from states.order_state import OrderState
from utils.utils import format_phone_number

order_router = Router()
order_router.message.filter(ChatTypeFilter(["private"]))


@order_router.callback_query(MenuCallBack.filter(F.menu_name == "order"))
async def start_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please enter your name:")
    await state.set_state(OrderState.name)
    await callback.answer()


@order_router.message(OrderState.name, F.text)
async def process_name(message: types.Message, state: FSMContext):
    if len(message.text) < 2 or len(message.text) > 50:
        await message.answer(
            "Name must be between 2 and 50 characters. Please enter your name again:"
        )
        return
    await state.update_data(name=message.text)
    await message.answer(
        "Please enter your phone number:", reply_markup=get_back_button()
    )
    await state.set_state(OrderState.phone)


@order_router.message(OrderState.phone, F.text)
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Back":
        await message.answer(
            "Please enter your name again:", reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(OrderState.name)
        return

    formatted_phone = format_phone_number(message.text)
    if not formatted_phone:
        await message.answer(
            "Invalid phone number. Please enter a valid phone number (10-15 digits):"
        )
        return

    await state.update_data(phone=formatted_phone)
    await message.answer(
        "Phone number accepted. Please enter your address:",
        reply_markup=get_back_button(),
    )
    await state.set_state(OrderState.address)


@order_router.message(OrderState.address, F.text)
async def process_address(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Back":
        await message.answer(
            "Please enter your phone number again:", reply_markup=get_back_button()
        )
        await state.set_state(OrderState.phone)
        return

    if len(message.text) < 5 or len(message.text) > 100:
        await message.answer(
            "Address must be between 5 and 100 characters. Please enter your address again:"
        )
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
                InlineKeyboardButton(text="Cancel ❌", callback_data="cancel_order"),
            ]
        ]
    )

    await message.answer(confirmation_message, reply_markup=keyboard)
    await state.set_state(OrderState.confirm)


@order_router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        await callback.answer("This order has already been processed!", show_alert=True)
        return

    try:
        user_data = await state.get_data()

        cart_items = await get_cart_items(callback.from_user.id)

        if not cart_items:
            await callback.answer("Your cart is empty!", show_alert=True)
            return

        await add_order_with_items(
            user_id=callback.from_user.id,
            name=user_data.get("name", ""),
            phone=user_data.get("phone", ""),
            address=user_data.get("address", ""),
            status="pending",
            cart_items=cart_items,
        )

        await clear_cart(user_id=callback.from_user.id)

        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            "Your order has been confirmed! ✅\n"
            "You can view your order details in the Orders menu.",
            reply_markup=get_user_main_btns(level=1),
        )

        await state.clear()
        await callback.answer("Order successfully created!", show_alert=True)

    except (FileNotFoundError, AttributeError, OSError, TypeError):

        await callback.answer(
            "Error creating order. Please try again.", show_alert=True
        )


@order_router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer("This order has already been processed!", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

    await callback.message.answer(
        "Order canceled ❌", reply_markup=ReplyKeyboardRemove()
    )

    await state.clear()


@order_router.callback_query(F.data.startswith("edit_"))
async def handle_edit(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[1]
    if field == "name":
        await callback.message.answer(
            "Please enter your name again:", reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(OrderState.name)
    elif field == "phone":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⬅️ Back")],
            ],
            resize_keyboard=True,
        )
        await callback.message.answer(
            "Please enter your phone number again:", reply_markup=keyboard
        )
        await state.set_state(OrderState.phone)
    elif field == "address":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⬅️ Back")],
            ],
            resize_keyboard=True,
        )
        await callback.message.answer(
            "Please enter your address again:", reply_markup=keyboard
        )
        await state.set_state(OrderState.address)

    await callback.answer()


@order_router.message(Command("orders"))
@order_router.callback_query(MenuCallBack.filter(F.menu_name == "orders"))
async def process_orders_command(update: Union[CallbackQuery, Message]):
    try:
        if isinstance(update, CallbackQuery):
            user_id = update.from_user.id
            target = update.message
            is_callback = True
        else:
            user_id = update.from_user.id
            target = update
            is_callback = False

        orders = await get_user_orders(user_id)

        banner = await get_banner("orders")
        if not banner:
            raise ValueError("Banner not found")

        if not banner.image:
            raise ValueError("Banner has no image")

        image_path = os.path.join(settings.MEDIA_ROOT, str(banner.image))
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Banner image not found: {image_path}")

        if not orders:
            pass
        else:
            text = ""
            for order in orders:
                text += (
                    f"🔸 Заказ {str(order.id)[:8]}\n"
                    f"👤 Имя: {order.name}\n"
                    f"📦 Статус: {order.status}\n"
                    f"📍 Адрес: {order.address}\n"
                    f"📱 Телефон: {order.phone}\n"
                    f"-------------------\n"
                )

            media = InputMediaPhoto(
                media=FSInputFile(image_path),
                caption=f"<strong>{banner.description}</strong>\n\n{text}",
                parse_mode="HTML",
            )

            keyboard = get_order_details_keyboard(orders)

            if is_callback:
                await target.edit_media(media=media, reply_markup=keyboard)
                await update.answer()
            else:
                await target.answer_photo(
                    photo=FSInputFile(image_path),
                    caption=f"<strong>{banner.description}</strong>\n\n{text}",
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

    except (FileNotFoundError, AttributeError, OSError, TypeError):
            await update.answer(
                "There was an error retrieving order details", show_alert=True
            )


@order_router.message(Command("orders"))
@order_router.callback_query(MenuCallBack.filter(F.menu_name == "orders"))
async def process_orders_command(update: Union[CallbackQuery, Message]):
    try:
        if isinstance(update, CallbackQuery):
            user_id = update.from_user.id
            target = update.message
            is_callback = True
        else:
            user_id = update.from_user.id
            target = update
            is_callback = False

        orders = await get_user_orders(user_id)

        banner = await get_banner("orders")
        if not banner:
            raise ValueError("Banner not found")

        if not banner.image:
            raise ValueError("Banner has no image")

        image_path = os.path.join(settings.MEDIA_ROOT, str(banner.image))
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Banner image not found: {image_path}")

        if not orders:
            pass
        else:
            text = ""
            for order in orders:
                text += (
                    f"🔸 Order {str(order.id)[:8]}\n"
                    f"👤 Name: {order.name}\n"
                    f"📦 Status: {order.status}\n"
                    f"📍 Address: {order.address}\n"
                    f"📱 Phone: {order.phone}\n"
                    f"-------------------\n"
                )

            media = InputMediaPhoto(
                media=FSInputFile(image_path),
                caption=f"<strong>{banner.description}</strong>\n\n{text}",
                parse_mode="HTML",
            )

            keyboard = get_order_details_keyboard(orders)

            if is_callback:
                await target.edit_media(media=media, reply_markup=keyboard)
                await update.answer()
            else:
                await target.answer_photo(
                    photo=FSInputFile(image_path),
                    caption=f"<strong>{banner.description}</strong>\n\n{text}",
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

    except (FileNotFoundError, AttributeError, OSError, TypeError):
            await update.answer(
                "There was an error retrieving order details", show_alert=True
            )


@order_router.callback_query(OrderDetailCallBack.filter())
async def process_order_detail(
    callback: CallbackQuery, callback_data: OrderDetailCallBack
):
    try:
        order = await get_order_by_id(callback_data.order_id)
        if not order:
            await callback.answer("Order not found", show_alert=True)
            return

        items = await get_order_items(order.id)

        if not items:
            await callback.answer("The order has no products", show_alert=True)
            return

        total_sum = sum(float(item.price) * item.quantity for item in items)

        text = (
            f"📋 Order Detail {str(order.id)[:8]}\n"
            f"📅 Creation date: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"👤 First name: {order.name}\n"
            f"📦 Status: {order.status}\n"
            f"📍 Address: {order.address}\n"
            f"📱 Phone: {order.phone}\n\n"
            f"📝 Items in order:\n\n"
        )

        for item in items:
            text += (
                f" {item.product.name}\n"
                f" Quantity: {item.quantity} \n"
                f" Price: {item.price:.2f} 💵\n"
                f"-------------------\n"
            )

        text += f"\n💰 Total price: {total_sum:.2f}"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="◀️ Back to orders",
                        callback_data=MenuCallBack(menu_name="orders", level=1).pack(),
                    )
                ]
            ]
        )

        banner = await get_banner("orders")
        if banner and banner.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(banner.image))

            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=FSInputFile(image_path), caption=text, parse_mode="HTML"
                ),
                reply_markup=keyboard,
            )
        else:
            await callback.message.edit_text(
                text=text, parse_mode="HTML", reply_markup=keyboard
            )

        await callback.answer()

    except (FileNotFoundError, AttributeError, OSError, TypeError):
        await callback.answer(
            "There was an error retrieving order details", show_alert=True
        )
