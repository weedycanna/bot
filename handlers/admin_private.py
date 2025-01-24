import os

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from django.conf import settings

from app import bot
from filters.chat_types import ChatTypeFilter, IsAdmin
from keybords.inline import get_callback_btns
from keybords.reply import get_keyboard
from queries.banner_queries import change_banner_image, get_info_pages
from queries.user_queries import total_users
from queries.category_queries import get_categories
from queries.products_queries import (
    add_product,
    delete_product,
    get_product,
    get_products,
    update_product,
)
from states.banner_state import AddBanner
from states.product_state import AddProduct


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "➕ Add good",
    "🛒 Assortment",
    "🖼️ Add/Change banner",
    "📊 Statistics",
    "📣 Newsletter",
    placeholder="What do you want to do?",
    sizes=(2,),
)


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message) -> None:
    await message.answer("What do you want to do?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "🛒 Assortment")
async def assortment(message: types.Message):
    categories = await get_categories()
    btns = {category.name: f"category_{category.id}" for category in categories}
    await message.answer(
        "Choose the category:", reply_markup=get_callback_btns(btns=btns)
    )


@admin_router.message(F.text == "📊 Statistics")
async def show_statistics(message: types.Message):
    user_id = message.from_user.id
    if user_id not in bot.my_admins_list:
        await message.answer("❌ You do not have sufficient rights to access this feature.")
        return

    users = await total_users()

    await message.answer(f"📊 Statistics:\n👥 Total users: {users}")



@admin_router.callback_query(F.data.startswith("category_"))
async def starring_at_product(callback: types.CallbackQuery):
    try:
        category_id = callback.data.split("_")[-1]
        products = await get_products(int(category_id))

        for product in products:
            try:
                if product.image and hasattr(product.image, "path"):
                    image_path = product.image.path
                    if os.path.exists(image_path):
                        photo = FSInputFile(image_path)
                        await callback.message.answer_photo(
                            photo=photo,
                            caption=f"<strong>{product.name}</strong>\n{product.description}\n"
                            f"Price: {round(product.price, 2)}💵",
                            reply_markup=get_callback_btns(
                                btns={
                                    "Delete": f"delete_{product.id}",
                                    "Edit": f"edit_{product.id}",
                                },
                                sizes=(2,),
                            ),
                        )
                else:
                    await callback.message.answer(
                        f"<strong>{product.name}</strong>\n{product.description}\n"
                        f"Price: {round(product.price, 2)}💵",
                        reply_markup=get_callback_btns(
                            btns={
                                "Delete": f"delete_{product.id}",
                                "Edit": f"edit_{product.id}",
                            },
                            sizes=(2,),
                        ),
                    )
            except (FileNotFoundError, AttributeError, OSError, TypeError):
                continue

        await callback.answer()
        await callback.message.answer("Ok, list of products ⏫")

    except (FileNotFoundError, AttributeError, OSError, TypeError):
        await callback.message.answer("Error occurred while processing products")
        await callback.answer()


@admin_router.callback_query(F.data.startswith("delete_"))
async def get_delete_product(callback: types.CallbackQuery):
    product_id = callback.data.split("_")[-1]
    await delete_product(int(product_id))

    animation_url: str = "https://media.giphy.com/media/h3oEjI6SIIHBdRxXI40/giphy.gif"
    await callback.message.answer_animation(animation=animation_url)

    await callback.answer("Good deleted successfully!")
    await callback.message.answer("Good deleted successfully!")


@admin_router.message(StateFilter(None), F.text == "🖼️ Add/Change banner")
async def add_image_to_banner(message: types.Message, state: FSMContext) -> None:
    pages_names = [page.name for page in await get_info_pages()]
    await message.answer(
        f"Send a banner photo. \n Choose the page for the banner:  \n {', '.join(pages_names)}"
    )
    await state.set_state(AddBanner.image)


@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext) -> None:
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await get_info_pages()]
    if for_page not in pages_names:
        await message.answer(
            "You write wrong page name, please choose the page from the list"
        )
        return
    await change_banner_image(
        for_page,
        image_id,
    )
    await message.answer("Banner added/changed successfully!")
    await state.clear()


@admin_router.message(AddBanner.image, or_f(F.photo, F.text == "."))
async def not_correct_add_banner(message: types.Message) -> None:
    await message.answer("You write wrong data, please load the image of the banner:")


@admin_router.callback_query(StateFilter(None), F.data.startswith("edit_"))
async def edit_product_callback(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.split("_")[-1]
    product_for_change = await get_product(int(product_id))

    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        "Enter the name of the product you want to change:",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter(None), F.text == "➕ Add good")
async def get_add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Enter the name of the product you want to add:",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter("*"), Command("cancel"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "cancel")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if AddProduct.product_for_change:
        AddProduct.product_for_change = None

    await state.clear()
    await message.answer("Canceled", reply_markup=ADMIN_KB)


@admin_router.message(StateFilter("*"), Command("back"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "back")
async def back_step_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == AddProduct.name:
        await message.answer('Previous step is not available, or write "cancel"')
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ok, you are on the previous step \n {AddProduct.texts[previous.state]}"
            )
            return
        previous = step


@admin_router.message(AddProduct.name, or_f(F.text, F.text == "."))
async def add_name(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        if 4 >= len(message.text) >= 100:
            await message.answer(
                "Product name is too long or too short, please write the name of the product:"
            )
            return

        await state.update_data(name=message.text)
    await message.answer("Enter the description of the product:")
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def not_correct_add_name(message: types.Message, state: FSMContext):
    await message.answer("You write wrong data, please write the name of the product:")


@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        if 4 >= len(message.text) <= 1000:
            await message.answer(
                "Product description is too long or too short, \n please write the description of the product:"
            )
            return

        await state.update_data(description=message.text)

    categories = await get_categories()
    btns = {category.name: str(category.id) for category in categories}
    await message.answer(
        "Choose the category:", reply_markup=get_callback_btns(btns=btns)
    )
    await state.set_state(AddProduct.category)


@admin_router.message(AddProduct.description)
async def not_correct_add_description(message: types.Message, state: FSMContext):
    await message.answer(
        "You write wrong data, please write the description of the product:"
    )


@admin_router.callback_query(AddProduct.category)
async def category_choice(callback: types.CallbackQuery, state: FSMContext):
    if int(callback.data) in [category.id for category in await get_categories()]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer("Enter the price of the product:")
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer("Choose the category from the list")
        await callback.answer()


@admin_router.message(AddProduct.category)
async def not_correct_category_choice(message: types.Message, state: FSMContext):
    await message.answer(
        "You write wrong data, please choose the category from the list:"
    )


@admin_router.message(AddProduct.price)
async def add_price(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("Write correct data, digit only")
            return

        await state.update_data(price=message.text)
    await message.answer("Load the image of the product:")
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def not_correct_add_price(message: types.Message, state: FSMContext):
    await message.answer("You write wrong data, please write the price of the product:")


@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext):
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

            file_name = f"product_{int(message.date.timestamp())}.jpg"
            save_path = os.path.join("products", file_name)
            full_path = os.path.join(settings.MEDIA_ROOT, save_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            await message.bot.download_file(
                file_path=file.file_path, destination=full_path
            )
            await state.update_data(image=save_path)
        else:
            await message.answer("Send a photo or '.' to keep the current image")
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

        await message.answer(
            "Product added/updated successfully!", reply_markup=ADMIN_KB
        )
        await state.clear()
        AddProduct.product_for_change = None

    except (FileNotFoundError, AttributeError, OSError, TypeError):
        await message.answer(
            "Error occurred. Try again or type 'cancel'", reply_markup=ADMIN_KB
        )
        await state.clear()
        AddProduct.product_for_change = None


@admin_router.message(AddProduct.image)
async def not_correct_add_image(message: types.Message, state: FSMContext):
    await message.answer("You write wrong data, please load the image of the product:")
