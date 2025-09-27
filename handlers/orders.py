import asyncio
import os
from datetime import datetime, timedelta
from textwrap import dedent
from typing import Union

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, FSInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup, InputMediaPhoto, Invoice,
                           KeyboardButton, LabeledPrice, Message,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove)
from django.conf import settings
from app_config import bot_messages

from app import crypto_client
from callbacks.callbacks import OrderDetailCallBack
from filters.chat_types import ChatTypeFilter
from handlers.payment import CryptoApiManager
from keybords.inline import (MenuCallBack, get_order_details_keyboard,
                             get_select_payment_keyboard, get_user_main_btns)
from keybords.reply import get_back_button
from queries.banner_queries import get_banner
from queries.cart_queries import clear_cart, get_cart_items
from queries.order_queries import (add_order_with_items, get_order_by_id,
                                   get_order_items, get_order_status,
                                   get_user_orders)
from states.order_state import OrderState
from utils.utils import format_phone_number

order_router = Router()
order_router.message.filter(ChatTypeFilter(["private"]))


@order_router.callback_query(MenuCallBack.filter(F.menu_name == "order"))
async def start_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(bot_messages.get("first_name_request"))
    await state.set_state(OrderState.name)
    await callback.answer()


@order_router.message(OrderState.name, F.text)
async def process_name(message: types.Message, state: FSMContext):
    if len(message.text) < 2 or len(message.text) > 50:
        await message.answer(
            bot_messages.get("name_length_error")
        )
        return
    await state.update_data(name=message.text)
    await message.answer(
        bot_messages.get("phone_request_order"), reply_markup=get_back_button()
    )
    await state.set_state(OrderState.phone)


@order_router.message(OrderState.phone, F.text)
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == bot_messages.get("back_button"):
        await message.answer(
            bot_messages.get("name_request_again"), reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(OrderState.name)
        return

    formatted_phone = format_phone_number(message.text)
    if not formatted_phone:
        await message.answer(
            bot_messages.get("invalid_phone_format_order")
        )
        return

    await state.update_data(phone=formatted_phone)
    await message.answer(
        bot_messages.get("phone_accepted_address_request"),
        reply_markup=get_back_button(),
    )
    await state.set_state(OrderState.address)


@order_router.message(OrderState.address, F.text)
async def process_address(message: types.Message, state: FSMContext):
    if message.text == bot_messages.get("back_button"):
        await message.answer(
            bot_messages.get("phone_request_again"), reply_markup=get_back_button()
        )
        await state.set_state(OrderState.phone)
        return

    if len(message.text) < 5 or len(message.text) > 100:
        await message.answer(
            bot_messages.get("address_length_error")
        )
        return

    await state.update_data(address=message.text)
    user_data = await state.get_data()

    cart_items = await get_cart_items(message.from_user.id)
    total_amount = sum(float(item.product.price) * item.quantity for item in cart_items)

    confirmation_message = bot_messages.get("order_confirmation",
                                          name=user_data['name'],
                                          phone=user_data['phone'],
                                          address=user_data['address'],
                                          total_amount=total_amount)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=bot_messages.get("select_payment_btn"), callback_data="select_payment"),
                InlineKeyboardButton(text=bot_messages.get("cancel_order_btn"), callback_data="cancel_order"),
            ],
            [InlineKeyboardButton(text=bot_messages.get("user_agreement_btn"), url=os.getenv("USER_AGREEMENT"))]
        ]
    )

    await message.answer(confirmation_message, reply_markup=keyboard, parse_mode="HTML")
    await state.update_data(amount_usd=float(total_amount))
    await state.set_state(OrderState.payment)


@order_router.callback_query(F.data.startswith("select_payment"))
async def select_payment_method(callback: CallbackQuery, state: FSMContext):

    keyboard = get_select_payment_keyboard()

    await callback.message.edit_text(bot_messages.get("select_payment_method"), reply_markup=keyboard, parse_mode="HTML")


@order_router.callback_query(F.data.startswith("crypto_"))
async def process_crypto_payment(callback: CallbackQuery, state: FSMContext):
    try:
        user_data = await state.get_data()
        amount_usd = user_data.get("amount_usd")
        crypto = callback.data.split("_")[1]

        try:
            rate = await CryptoApiManager.get_crypto_rate(crypto, "USD")

            if rate is None:
                await callback.answer(bot_messages.get("crypto_rate_error"), show_alert=True)
                return

            crypto_amount = await CryptoApiManager.convert_to_crypto(float(amount_usd), "USD", crypto)

            if crypto_amount is None:
                await callback.answer(bot_messages.get("crypto_calculation_error"), show_alert=True)
                return

            invoice = await crypto_client.create_invoice(
                asset=crypto, amount=crypto_amount, description=bot_messages.get("order_payment_description", user_id=callback.from_user.id)
            )
        except Exception as e:
            await callback.answer(bot_messages.get("crypto_invoice_error"), show_alert=True)
            return

        if not invoice or not hasattr(invoice, "invoice_id") or not hasattr(invoice, "bot_invoice_url"):
            await callback.answer(bot_messages.get("invalid_payment_response"), show_alert=True)
            return

        expiration_time = datetime.now() + timedelta(minutes=3)

        try:
            await state.update_data(
                {
                    "invoice_id": invoice.invoice_id,
                    "payment_crypto": crypto,
                    "expiration_time": expiration_time.timestamp(),
                }
            )
        except Exception as e:
            await callback.answer(bot_messages.get("payment_data_save_error"), show_alert=True)
            return

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=bot_messages.get("pay_with_crypto_btn", crypto=crypto), url=invoice.bot_invoice_url)],
                [InlineKeyboardButton(text=bot_messages.get("cancel_order_btn"), callback_data="cancel_order")],
            ]
        )

        if crypto == "USDT":
            crypto_format = f"{crypto_amount:.2f}"
        else:
            crypto_format = f"{crypto_amount:.8f}"

        payment_message = bot_messages.get("payment_details",
                                         amount_usd=amount_usd,
                                         crypto_amount=crypto_format,
                                         crypto=crypto,
                                         expiration_time=expiration_time.strftime('%H:%M:%S'))

        try:
            await callback.message.edit_text(payment_message, reply_markup=keyboard, parse_mode="HTML")
        except Exception as e:
            await callback.answer(bot_messages.get("payment_details_display_error"), show_alert=True)
            return

        asyncio.create_task(
            check_payment(invoice.invoice_id, callback.from_user.id, amount_usd, crypto, callback.bot, state, user_data)
        )

    except Exception as e:
        await callback.answer(bot_messages.get("payment_processing_error"), show_alert=True)
        return


@order_router.callback_query(F.data == "star_payment")
async def handle_star_payment(callback: CallbackQuery, state: FSMContext):
    try:
        user_data = await state.get_data()
        amount_usd = user_data.get('amount_usd')
        star_rate = 0.0187
        stars_amount = int(float(amount_usd) / star_rate)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=bot_messages.get("pay_with_stars_btn", stars_amount=stars_amount), pay=True)],
            [InlineKeyboardButton(text=bot_messages.get("cancel_order_btn"), callback_data="cancel_order")]
        ])

        prices = [LabeledPrice(label="XTR", amount=stars_amount)]
        expiration_time = datetime.now() + timedelta(minutes=3)
        payload = f"{amount_usd}_{stars_amount}_{expiration_time.strftime('%Y-%m-%d %H:%M:%S')}"

        await callback.bot.send_invoice(
            chat_id=callback.from_user.id,
            title=bot_messages.get("order_payment_title"),
            description=bot_messages.get("star_payment_description", stars_amount=stars_amount),
            prices=prices,
            provider_token=os.getenv("STAR_PAYMENT_TOKEN"),
            payload=payload,
            currency="XTR",
            protect_content=False,
            request_timeout=15,
            reply_markup=kb
        )

    except Exception:
        await callback.answer(bot_messages.get("star_payment_error"), show_alert=True)


async def check_payment(invoice_id, user_id, amount, crypto, bot, state, user_data):
    expiration_time = datetime.now() + timedelta(minutes=3)

    while datetime.now() < expiration_time:
        try:
            invoices = await crypto_client.get_invoices(invoice_ids=[invoice_id])
            if invoices and invoices[0].status == 'paid':
                try:
                    cart_items = await get_cart_items(user_id)

                    await clear_cart(user_id)

                    order = await add_order_with_items(
                        user_id=user_id,
                        name=user_data.get("name", ""),
                        phone=user_data.get("phone", ""),
                        address=user_data.get("address", ""),
                        status="completed",
                        cart_items=cart_items,
                    )

                    await clear_cart(user_id)

                    order_status = await get_order_status(order.id)

                    success_message = bot_messages.get("payment_successful",
                                                    order_id=order.id,
                                                    order_status=order_status,
                                                    amount=amount,
                                                    crypto=crypto,
                                                    name=user_data.get("name", ""),
                                                    phone=user_data.get("phone", ""),
                                                    address=user_data.get("address", ""))

                    await bot.send_message(
                        user_id,
                        success_message,
                        reply_markup=get_user_main_btns(level=1),
                        parse_mode="HTML"
                    )
                    await state.clear()
                    return
                except Exception:
                    await bot.send_message(
                        user_id,
                        bot_messages.get("payment_received_order_failed"),
                        parse_mode="HTML"
                    )
                    return

            await asyncio.sleep(5)
        except Exception:
            await asyncio.sleep(5)
            continue

    await bot.send_message(
        user_id,
        bot_messages.get("payment_time_expired"),
        parse_mode="HTML"
    )
    await state.clear()


@order_router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer(bot_messages.get("order_already_processed"), show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

    await callback.message.answer(
        bot_messages.get("order_canceled"), reply_markup=ReplyKeyboardRemove()
    )

    await state.clear()


@order_router.callback_query(F.data.startswith("edit_"))
async def handle_edit(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[1]
    if field == "name":
        await callback.message.answer(
            bot_messages.get("name_request_again"), reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(OrderState.name)
    elif field == "phone":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=bot_messages.get("back_button"))],
            ],
            resize_keyboard=True,
        )
        await callback.message.answer(
            bot_messages.get("phone_request_again"), reply_markup=keyboard
        )
        await state.set_state(OrderState.phone)
    elif field == "address":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=bot_messages.get("back_button"))],
            ],
            resize_keyboard=True,
        )
        await callback.message.answer(
            bot_messages.get("address_request_again"), reply_markup=keyboard
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
            raise ValueError(bot_messages.get("banner_not_found"))

        if not banner.image:
            raise ValueError(bot_messages.get("banner_no_image"))

        image_path = os.path.join(settings.MEDIA_ROOT, str(banner.image))
        if not os.path.exists(image_path):
            raise FileNotFoundError(bot_messages.get("banner_image_not_found", path=image_path))

        if not orders:
            text = bot_messages.get("no_orders")
        else:
            text = ""
            for order in orders:
                text += bot_messages.get("order_item",
                                     order_id=str(order.id)[:8],
                                     name=order.name,
                                     status=order.status,
                                     address=order.address,
                                     phone=order.phone)

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
                bot_messages.get("order_details_error"), show_alert=True
            )


@order_router.callback_query(OrderDetailCallBack.filter())
async def process_order_detail(
        callback: CallbackQuery, callback_data: OrderDetailCallBack
):
    try:
        order = await get_order_by_id(callback_data.order_id)
        if not order:
            await callback.answer(bot_messages.get("order_not_found"), show_alert=True)
            return

        items = await get_order_items(order.id)

        if not items:
            await callback.answer(bot_messages.get("order_no_products"), show_alert=True)
            return

        total_sum = sum(float(item.price) * item.quantity for item in items)

        text = bot_messages.get("order_detail_header",
                              order_id=str(order.id)[:8],
                              created_at=order.created_at.strftime('%d.%m.%Y %H:%M'),
                              name=order.name,
                              status=order.status,
                              address=order.address,
                              phone=order.phone)

        for item in items:
            text += bot_messages.get("order_detail_item",
                                  name=item.product.name,
                                  quantity=item.quantity,
                                  price=item.price)

        text += bot_messages.get("order_detail_total", total_sum=total_sum)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=bot_messages.get("back_to_orders_btn"),
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
            bot_messages.get("order_details_error"), show_alert=True
        )