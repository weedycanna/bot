import os
import textwrap
from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, ReplyKeyboardRemove
from django.conf import settings
from fluentogram import TranslatorRunner

from app import bot
from django_project.telegrambot.usersmanage.models import TelegramUser
from filters.chat_types import ChatTypeFilter, IsAdmin
from filters.translated_text import TranslatedText
from keybords.inline import get_callback_btns
from keybords.reply import get_admin_keyboard
from queries.banner_queries import change_banner_image, get_info_pages
from queries.category_queries import get_categories
from queries.order_queries import total_orders
from queries.products_queries import (
    add_product,
    delete_product,
    get_product,
    get_products,
    total_products,
    total_products_by_category,
    update_product,
)
from queries.user_queries import total_users
from states.banner_state import AddBanner
from states.newsletter import Newsletter
from states.product_state import AddProduct

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message, i18n: TranslatorRunner) -> None:
    admin_kb = get_admin_keyboard(i18n)
    await message.answer(i18n.admin_kb_placeholder(), reply_markup=admin_kb)


@admin_router.message(TranslatedText("admin_assortment"))
async def assortment_text(message: types.Message, i18n: TranslatorRunner):
    categories = await get_categories()
    btns = {category.name: f"category_{category.id}" for category in categories}
    await message.answer(
        i18n.admin_choose_category(), reply_markup=get_callback_btns(btns=btns)
    )


@admin_router.message(TranslatedText("admin_statistics"))
async def show_statistics(message: types.Message, i18n: TranslatorRunner):
    users = await total_users()
    orders = await total_orders()
    products = await total_products()
    category_stats = await total_products_by_category()

    category_stats_lines = [
        f"{category}: {count}" for category, count in category_stats.items()
    ]
    category_stats_text = textwrap.indent("\n".join(category_stats_lines), "        ")

    await message.answer(
        i18n.admin_statistics_text(
            users=users,
            orders=orders,
            products=products,
            category_stats_text=category_stats_text,
        )
    )


@admin_router.callback_query(F.data.startswith("category_"))
async def starring_at_product(callback: types.CallbackQuery, i18n: TranslatorRunner):
    try:
        category_id = callback.data.split("_")[-1]
        products = await get_products(int(category_id))

        for product in products:
            try:
                caption = i18n.admin_product_card(
                    name=product.name,
                    description=product.description,
                    price=round(product.price, 2),
                )
                reply_markup = get_callback_btns(
                    btns={
                        i18n.admin_delete_btn(): f"delete_{product.id}",
                        i18n.admin_edit_btn(): f"edit_{product.id}",
                    },
                    sizes=(2,),
                )
                if product.image and hasattr(product.image, "path"):
                    image_path = product.image.path
                    if os.path.exists(image_path):
                        photo = FSInputFile(image_path)
                        await callback.message.answer_photo(
                            photo=photo,
                            caption=caption,
                            reply_markup=reply_markup,
                        )
                else:
                    await callback.message.answer(
                        caption,
                        reply_markup=reply_markup,
                    )
            except (FileNotFoundError, AttributeError, OSError, TypeError):
                continue

        await callback.answer()
        await callback.message.answer(i18n.admin_products_list())

    except (FileNotFoundError, AttributeError, OSError, TypeError):
        await callback.message.answer(i18n.admin_products_error())
        await callback.answer()


@admin_router.callback_query(F.data.startswith("delete_"))
async def get_delete_product(callback: types.CallbackQuery, i18n: TranslatorRunner):
    product_id = callback.data.split("_")[-1]
    await delete_product(int(product_id))

    animation_url: str = os.getenv("DELETE_ANIMATION_URL")
    if animation_url:
        await callback.message.answer_animation(animation=animation_url)

    await callback.answer(i18n.admin_product_deleted())
    await callback.message.answer(i18n.admin_product_deleted())


@admin_router.message(StateFilter(None), TranslatedText("admin_add_banner"))
async def add_image_to_banner(
    message: types.Message, state: FSMContext, i18n: TranslatorRunner
) -> None:
    pages_names = [page.name for page in await get_info_pages()]
    await message.answer(i18n.admin_banner_instructions(pages=", ".join(pages_names)))
    await state.set_state(AddBanner.image)


@admin_router.message(AddBanner.image, F.photo)
async def add_banner(
    message: types.Message, state: FSMContext, i18n: TranslatorRunner
) -> None:
    image_id = message.photo[-1].file_id
    if not message.caption:
        await message.answer(i18n.admin_banner_wrong_page())
        return

    for_page = message.caption.strip()
    pages_names = [page.name for page in await get_info_pages()]
    if for_page not in pages_names:
        await message.answer(i18n.admin_banner_wrong_page())
        return
    await change_banner_image(
        for_page,
        image_id,
    )
    await message.answer(i18n.admin_banner_success())
    await state.clear()


@admin_router.message(AddBanner.image, or_f(F.photo, F.text == "."))
async def not_correct_add_banner(
    message: types.Message, i18n: TranslatorRunner
) -> None:
    await message.answer(i18n.admin_banner_wrong_data())


@admin_router.callback_query(StateFilter(None), F.data.startswith("edit_"))
async def edit_product_callback(
    callback: types.CallbackQuery, state: FSMContext, i18n: TranslatorRunner
):
    product_id = callback.data.split("_")[-1]
    product_for_change = await get_product(int(product_id))

    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        i18n.admin_product_edit_name(),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter(None), TranslatedText("admin_add_good"))
async def get_add_product(
    message: types.Message, state: FSMContext, i18n: TranslatorRunner
):
    await message.answer(
        i18n.admin_product_add_name(),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter("*"), Command("cancel"))
async def cancel_handler(
    message: types.Message, state: FSMContext, i18n: TranslatorRunner
) -> None:
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None

    await state.clear()
    admin_kb = get_admin_keyboard(i18n)
    await message.answer(i18n.admin_canceled(), reply_markup=admin_kb)


@admin_router.message(StateFilter("*"), Command("back"))
async def back_step_handler(
    message: types.Message, state: FSMContext, i18n: TranslatorRunner
):
    current_state = await state.get_state()

    if current_state == AddProduct.name:
        await message.answer(i18n.admin_no_previous_step())
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            step_text = AddProduct.texts.get(previous.state, "")
            await message.answer(i18n.admin_previous_step(step_text=step_text))
            return
        previous = step


@admin_router.message(AddProduct.name, or_f(F.text, F.text == "."))
async def add_name(message: types.Message, state: FSMContext, i18n: TranslatorRunner):
    if message.text == ".":
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        if not (4 <= len(message.text) <= 100):
            await message.answer(i18n.admin_product_name_error())
            return

        await state.update_data(name=message.text)
    await message.answer(i18n.admin_product_description())
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def not_correct_add_name(message: types.Message, i18n: TranslatorRunner):
    await message.answer(i18n.admin_product_name_wrong_data())


@admin_router.message(AddProduct.description, F.text)
async def add_description(
    message: types.Message, state: FSMContext, i18n: TranslatorRunner
):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        if not (4 <= len(message.text) <= 1000):
            await message.answer(i18n.admin_product_description_error())
            return

        await state.update_data(description=message.text)

    categories = await get_categories()
    btns = {category.name: str(category.id) for category in categories}
    await message.answer(
        i18n.admin_choose_category(), reply_markup=get_callback_btns(btns=btns)
    )
    await state.set_state(AddProduct.category)


@admin_router.message(AddProduct.description)
async def not_correct_add_description(message: types.Message, i18n: TranslatorRunner):
    await message.answer(i18n.admin_product_description_wrong_data())


@admin_router.callback_query(AddProduct.category)
async def category_choice(
    callback: types.CallbackQuery, state: FSMContext, i18n: TranslatorRunner
):
    if int(callback.data) in [category.id for category in await get_categories()]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer(i18n.admin_product_price())
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer(i18n.admin_category_wrong_choice())
        await callback.answer()


@admin_router.message(AddProduct.category)
async def not_correct_category_choice(message: types.Message, i18n: TranslatorRunner):
    await message.answer(i18n.admin_category_wrong_data())


@admin_router.message(AddProduct.price)
async def add_price(message: types.Message, state: FSMContext, i18n: TranslatorRunner):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer(i18n.admin_price_error())
            return

        await state.update_data(price=message.text)
    await message.answer(i18n.admin_product_image())
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def not_correct_add_price(message: types.Message, i18n: TranslatorRunner):
    await message.answer(i18n.admin_product_price_wrong_data())


@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, i18n: TranslatorRunner):
    try:
        if message.text == "." and AddProduct.product_for_change:
            await state.update_data(
                image=(
                    AddProduct.product_for_change.image.name
                    if AddProduct.product_for_change.image
                    else None
                )
            )
        elif message.photo:
            photo = message.photo[-1]
            file = await message.bot.get_file(photo.file_id)

            file_name = f"product_{int(datetime.now().timestamp())}.jpg"
            save_path = os.path.join("products", file_name)
            full_path = os.path.join(settings.MEDIA_ROOT, save_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            await message.bot.download_file(
                file_path=file.file_path, destination=full_path
            )
            await state.update_data(image=save_path)
        else:
            await message.answer(i18n.admin_image_keep_current())
            return

        data = await state.get_data()

        if AddProduct.product_for_change:
            if "image" in data and AddProduct.product_for_change.image:
                old_image_path = AddProduct.product_for_change.image.path
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            await update_product(AddProduct.product_for_change.id, data)
        else:
            await add_product(data)

        admin_kb = get_admin_keyboard(i18n)
        await message.answer(i18n.admin_product_success(), reply_markup=admin_kb)
        await state.clear()
        AddProduct.product_for_change = None

    except (FileNotFoundError, AttributeError, OSError, TypeError):
        admin_kb = get_admin_keyboard(i18n)
        await message.answer(i18n.admin_product_error(), reply_markup=admin_kb)
        await state.clear()
        AddProduct.product_for_change = None


@admin_router.message(AddProduct.image)
async def not_correct_add_image(message: types.Message, i18n: TranslatorRunner):
    await message.answer(i18n.admin_product_image_wrong_data())


@admin_router.message(TranslatedText("admin_newsletter"))
async def newsletter(message: types.Message, state: FSMContext, i18n: TranslatorRunner):
    if message.from_user.id not in bot.my_admins_list:
        await message.answer(i18n.admin_no_access())
        return

    await state.set_state(Newsletter.waiting_for_content)
    await message.answer(i18n.admin_newsletter_content())


@admin_router.message(Newsletter.waiting_for_content)
async def process_newsletter(
    message: types.Message, state: FSMContext, i18n: TranslatorRunner
):
    users = TelegramUser.objects.all()
    start_time = datetime.now()
    success_count = 0
    error_count = 0
    for user in users:
        try:
            await bot.send_message(
                user.user_id, message.text, parse_mode=message.parse_mode
            )
            success_count += 1
        except Exception:
            error_count += 1
            continue

    time_taken = (datetime.now() - start_time).total_seconds()
    await message.answer(
        i18n.admin_newsletter_success(
            success_count=success_count,
            error_count=error_count,
            time_taken=f"{time_taken:.2f}",
        ),
        parse_mode="HTML",
    )

    await state.clear()
