import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton, LabeledPrice,
                           Message, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from fluentogram import TranslatorRunner

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
from utils.get_banner_image import get_banner_image
from utils.currency import convert_currency, format_price
from utils.phone_formatting import format_phone_number

order_router = Router()
order_router.message.filter(ChatTypeFilter(["private"]))


@order_router.callback_query(MenuCallBack.filter(F.menu_name == "order"))
async def start_order(
    callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner
) -> None:
    await callback.message.answer(i18n.first_name_request())
    await state.set_state(OrderState.name)
    await callback.answer()


@order_router.message(OrderState.name, F.text)
async def process_name(
    message: types.Message, state: FSMContext, i18n: TranslatorRunner
) -> None:
    if len(message.text) < 2 or len(message.text) > 50:
        await message.answer(i18n.name_length_error())
        return
    await state.update_data(name=message.text)
    await message.answer(
        i18n.phone_request_order(), reply_markup=get_back_button(i18n=i18n)
    )
    await state.set_state(OrderState.phone)


@order_router.message(OrderState.phone, F.text)
async def process_phone(
    message: types.Message, state: FSMContext, i18n: TranslatorRunner
):
    if message.text == i18n.back_button():
        await message.answer(
            i18n.name_request_again(), reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(OrderState.name)
        return

    formatted_phone = format_phone_number(message.text)
    if not formatted_phone:
        await message.answer(i18n.invalid_phone_format_order())
        return

    await state.update_data(phone=formatted_phone)
    await message.answer(
        i18n.phone_accepted_address_request(),
        reply_markup=get_back_button(i18n=i18n),
    )
    await state.set_state(OrderState.address)


@order_router.message(OrderState.address, F.text)
async def process_address(
    message: types.Message,
    state: FSMContext,
    i18n: TranslatorRunner,
    user_language: str,
):
    if message.text == i18n.back_button():
        await message.answer(
            i18n.phone_request_again(), reply_markup=get_back_button(i18n=i18n)
        )
        await state.set_state(OrderState.phone)
        return

    if len(message.text) < 5 or len(message.text) > 100:
        await message.answer(i18n.address_length_error())
        return

    await state.update_data(address=message.text)
    user_data = await state.get_data()

    cart_items = await get_cart_items(message.from_user.id)
    total_amount_usd = sum(
        float(item.product.price) * item.quantity for item in cart_items
    )

    total_amount, currency = await convert_currency(total_amount_usd, user_language)

    confirmation_message = i18n.order_confirmation(
        name=user_data["name"],
        phone=user_data["phone"],
        address=user_data["address"],
        total_amount=format_price(total_amount, currency),
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.select_payment_btn(), callback_data="select_payment"
                ),
                InlineKeyboardButton(
                    text=i18n.cancel_order_btn(), callback_data="cancel_order"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.user_agreement_btn(), url=os.getenv("USER_AGREEMENT")
                )
            ],
        ]
    )

    await message.answer(confirmation_message, reply_markup=keyboard, parse_mode="HTML")
    await state.update_data(amount_usd=float(total_amount_usd))
    await state.set_state(OrderState.payment)


@order_router.callback_query(F.data.startswith("select_payment"))
async def select_payment_method(
    callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner
):
    keyboard = get_select_payment_keyboard(i18n=i18n)

    await callback.message.edit_text(
        i18n.select_payment_method(), reply_markup=keyboard, parse_mode="HTML"
    )


@order_router.callback_query(F.data.startswith("crypto_"))
async def process_crypto_payment(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
    user_language: str,
):
    try:
        user_data = await state.get_data()
        amount_usd = user_data["amount_usd"]
        crypto = callback.data.split("_")[1]

        try:
            rate = await CryptoApiManager.get_crypto_rate(crypto, "USD")

            if rate is None:
                await callback.answer(i18n.crypto_rate_error(), show_alert=True)
                return

            crypto_amount = await CryptoApiManager.convert_to_crypto(
                float(amount_usd), "USD", crypto
            )

            if crypto_amount is None:
                await callback.answer(i18n.crypto_calculation_error(), show_alert=True)
                return

            invoice = await crypto_client.create_invoice(
                asset=crypto,
                amount=crypto_amount,
                description=i18n.order_payment_description(
                    user_id=str(callback.from_user.id)
                ),
            )
        except Exception:
            await callback.answer(i18n.crypto_invoice_error(), show_alert=True)
            return

        if (
            not invoice
            or not hasattr(invoice, "invoice_id")
            or not hasattr(invoice, "bot_invoice_url")
        ):
            await callback.answer(i18n.invalid_payment_response(), show_alert=True)
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
        except Exception:
            await callback.answer(i18n.payment_data_save_error(), show_alert=True)
            return

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.pay_with_crypto_btn(crypto=crypto),
                        url=invoice.bot_invoice_url,
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=i18n.cancel_order_btn(), callback_data="cancel_order"
                    )
                ],
            ]
        )

        if crypto == "USDT":
            crypto_format = f"{crypto_amount:.2f}"
        else:
            crypto_format = f"{crypto_amount:.8f}"

        display_amount, currency = await convert_currency(amount_usd, user_language)

        payment_message = i18n.payment_details(
            amount_usd=format_price(display_amount, currency),
            crypto_amount=crypto_format,
            crypto=crypto,
            expiration_time=expiration_time.strftime("%H:%M:%S"),
        )

        try:
            await callback.message.edit_text(
                payment_message, reply_markup=keyboard, parse_mode="HTML"
            )
        except Exception:
            await callback.answer(i18n.payment_details_display_error(), show_alert=True)
            return

        asyncio.create_task(
            check_payment(
                invoice.invoice_id,
                callback.from_user.id,
                amount_usd,
                crypto,
                callback.bot,
                state,
                user_data,
                i18n,
                user_language,
            )
        )

    except Exception:
        await callback.answer(i18n.payment_processing_error(), show_alert=True)
        return


@order_router.callback_query(F.data == "star_payment")
async def handle_star_payment(
    callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner
):
    try:
        user_data = await state.get_data()
        amount_usd = user_data["amount_usd"]

        star_rate = 0.0187
        stars_amount = int(float(amount_usd) / star_rate)

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.pay_with_stars_btn(stars_amount=stars_amount),
                        pay=True,
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=i18n.cancel_order_btn(), callback_data="cancel_order"
                    )
                ],
            ]
        )

        prices = [LabeledPrice(label="XTR", amount=stars_amount)]
        expiration_time = datetime.now() + timedelta(minutes=3)
        payload = f"{amount_usd}_{stars_amount}_{expiration_time.strftime('%Y-%m-%d %H:%M:%S')}"

        await callback.bot.send_invoice(
            chat_id=callback.from_user.id,
            title=i18n.order_payment_title(),
            description=i18n.star_payment_description(stars_amount=stars_amount),
            prices=prices,
            provider_token=os.getenv("STAR_PAYMENT_TOKEN"),
            payload=payload,
            currency="XTR",
            protect_content=False,
            request_timeout=15,
            reply_markup=kb,
        )

    except Exception:
        await callback.answer(i18n.star_payment_error(), show_alert=True)


async def check_payment(
    invoice_id,
    user_id,
    amount,
    crypto,
    bot,
    state,
    user_data,
    i18n: TranslatorRunner,
    user_language: str,
):
    expiration_time = datetime.now() + timedelta(minutes=3)

    while datetime.now() < expiration_time:
        try:
            invoices = await crypto_client.get_invoices(invoice_ids=[invoice_id])
            if invoices and invoices[0].status == "paid":
                try:
                    cart_items = await get_cart_items(user_id)
                    order = await add_order_with_items(
                        user_id=user_id,
                        name=user_data["name"],
                        phone=user_data["phone"],
                        address=user_data["address"],
                        status="completed",
                        cart_items=cart_items,
                    )
                    await clear_cart(user_id)
                    order_status = await get_order_status(order.id)

                    display_amount, currency = await convert_currency(
                        float(amount), user_language
                    )

                    success_message = i18n.payment_successful(
                        order_id=str(order.id),
                        order_status=order_status,
                        amount=format_price(display_amount, currency),
                        crypto=crypto,
                        name=user_data["name"],
                        phone=user_data["phone"],
                        address=user_data["address"],
                    )

                    main_menu_keyboard = get_user_main_btns(level=1, i18n=i18n)

                    temp_msg = await bot.send_message(
                        user_id, "...", reply_markup=ReplyKeyboardRemove()
                    )
                    await bot.delete_message(user_id, temp_msg.message_id)

                    await bot.send_message(
                        user_id,
                        success_message,
                        reply_markup=main_menu_keyboard,
                        parse_mode="HTML",
                    )

                    await state.clear()
                    return

                except Exception:
                    await bot.send_message(
                        user_id, i18n.payment_received_order_failed(), parse_mode="HTML"
                    )
                    return

            await asyncio.sleep(5)
        except Exception:
            await asyncio.sleep(5)
            continue

    await bot.send_message(user_id, i18n.payment_time_expired(), parse_mode="HTML")
    await state.clear()


@order_router.callback_query(F.data == "cancel_order")
async def cancel_order(
    callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner
):
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer(i18n.order_already_processed(), show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

    await callback.message.answer(
        i18n.order_canceled(), reply_markup=ReplyKeyboardRemove()
    )

    await state.clear()


@order_router.callback_query(F.data.startswith("edit_"))
async def handle_edit(
    callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner
):
    field = callback.data.split("_")[1]
    if field == "name":
        await callback.message.answer(
            i18n.name_request_again(), reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(OrderState.name)
    elif field == "phone":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=i18n.back_button())],
            ],
            resize_keyboard=True,
        )
        await callback.message.answer(i18n.phone_request_again(), reply_markup=keyboard)
        await state.set_state(OrderState.phone)
    elif field == "address":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=i18n.back_button())],
            ],
            resize_keyboard=True,
        )
        await callback.message.answer(
            i18n.address_request_again(), reply_markup=keyboard
        )
        await state.set_state(OrderState.address)

    await callback.answer()


@order_router.message(Command("orders"))
@order_router.callback_query(MenuCallBack.filter(F.menu_name == "orders"))
async def process_orders_command(
    update: Union[CallbackQuery, Message],
    i18n: TranslatorRunner,
    user_language: str,
):
    try:
        user_id = update.from_user.id
        target = update.message if isinstance(update, CallbackQuery) else update

        banner = await get_banner("orders", user_language)
        orders = await get_user_orders(user_id)

        if not orders:
            orders_list_text = i18n.no_orders()
        else:
            order_items = [
                i18n.order_item(
                    order_id=str(order.id)[:8],
                    name=str(order.name),
                    status=str(order.status),
                    address=str(order.address),
                    phone=str(order.phone),
                )
                for order in orders
            ]
            orders_list_text = "\n".join(order_items)

        header_text = ""
        if banner and banner.description:
            header_text = f"<strong>{banner.description}</strong>\n\n"

        final_caption = f"{header_text}{orders_list_text}"

        if not banner or not hasattr(banner.image, "path"):
            if isinstance(update, CallbackQuery):
                await update.message.edit_text(final_caption, parse_mode="HTML")
            else:
                await target.answer(final_caption, parse_mode="HTML")
            return

        media = types.InputMediaPhoto(
            media=types.FSInputFile(path=banner.image.path),
            caption=final_caption,
            parse_mode="HTML",
        )

        keyboard = get_order_details_keyboard(orders, i18n)

        if isinstance(update, CallbackQuery):
            await target.edit_media(media=media, reply_markup=keyboard)
            await update.answer()
        else:
            await target.answer_photo(
                photo=media.media,
                caption=media.caption,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
    except Exception:
        error_message = i18n.order_details_error()
        if isinstance(update, CallbackQuery):
            await update.answer(error_message, show_alert=True)
        else:
            await update.message.answer(error_message)


@order_router.callback_query(OrderDetailCallBack.filter())
async def process_order_detail(
    callback: CallbackQuery,
    callback_data: OrderDetailCallBack,
    i18n: TranslatorRunner,
    user_language: str,
):
    try:
        order = await get_order_by_id(callback_data.order_id)
        if not order:
            await callback.answer(i18n.order_not_found(), show_alert=True)
            return

        items = await get_order_items(order.id)
        if not items:
            await callback.answer(i18n.order_no_products(), show_alert=True)
            return

        total_sum_usd = sum(float(item.price) * item.quantity for item in items)
        total_sum, currency = await convert_currency(total_sum_usd, user_language)

        item_details_list = []
        for item in items:
            item_price_usd = float(item.price)
            item_price, item_currency = await convert_currency(
                item_price_usd, user_language
            )

            item_details_list.append(
                i18n.order_detail_item(
                    name=item.product.name,
                    quantity=int(item.quantity),
                    price=format_price(item_price, item_currency),
                )
            )

        final_text = (
            f"{i18n.order_detail_header(order_id=str(order.id)[:8], created_at=order.created_at.strftime('%d.%m.%Y %H:%M'), name=order.name, status=order.status, address=order.address, phone=str(order.phone))}"
            f"\n\n"
            f"{'\n'.join(item_details_list)}"
            f"\n\n"
            f"{i18n.order_detail_total(total_sum=format_price(total_sum, currency))}"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.back_to_orders_btn(),
                        callback_data=MenuCallBack(menu_name="orders", level=1).pack(),
                    )
                ]
            ]
        )

        try:
            media = await get_banner_image("orders", i18n)
            media.caption = final_text
            await callback.message.edit_media(media=media, reply_markup=keyboard)
        except (ValueError, FileNotFoundError):
            await callback.message.edit_text(
                text=final_text, parse_mode="HTML", reply_markup=keyboard
            )

        await callback.answer()

    except Exception:
        await callback.answer(i18n.order_details_error(), show_alert=True)
