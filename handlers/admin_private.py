

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession


from filters.chat_types import ChatTypeFilter, IsAdmin
from keybords.inline import get_callback_btns
from keybords.reply import get_keyboard
from queries.admin_queries import orm_get_products, orm_delete_product, orm_get_product, orm_update_product, \
    orm_add_product
from queries.banner_queries import orm_get_info_pages, orm_change_banner_image
from queries.category_queries import orm_get_categories

from states.banner_state import AddBanner
from states.product_state import AddProduct

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = get_keyboard(
    "Add good",
    "Assortment",
    "Add/Change banner",
    placeholder="What do you want to do?",
    sizes=(2,),
)

@admin_router.message(Command("admin"))
async def admin_features(message: types.Message) -> None:
    await message.answer("What do you want to do?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Assortment")
async def assortment(message: types.Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    await message.answer(
        "Choose the category:", reply_markup=get_callback_btns(btns=btns)
    )

@admin_router.callback_query(F.data.startswith("category_"))
async def starring_at_product(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split("_")[-1]
    print(f"Callback triggered for category_id: {category_id}")

    products = await orm_get_products(session, int(category_id))
    print(f"Products fetched for category {category_id}: {products}")

    for product in products:
        await callback.message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}</strong>\n{product.description}\nPrice: {round(product.price, 2)}💵",
            reply_markup=get_callback_btns(
                btns={
                    "Delete": f"delete_{product.id}",
                    "Edit": f"edit_{product.id}",
                },
                sizes=(2,),
            ),
        )
    await callback.answer()
    await callback.message.answer("Ok, list of products ⏫")


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))

    animation_url = "h3oEjI6SIIHBdRxXI40/giphy.gif"
    await callback.message.answer_animation(animation=animation_url)

    await callback.answer("Good deleted successfully!")
    await callback.message.answer("Good deleted successfully!")


@admin_router.message(StateFilter(None), F.text == "Add/Change banner")
async def add_image_to_banner(
    message: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(
        f"Send a banner photo. \n Choose the page for the banner:  \n {', '.join(pages_names)}"
    )
    await state.set_state(AddBanner.image)


@admin_router.message(AddBanner.image, F.photo)
async def add_banner(
    message: types.Message, state: FSMContext, session: AsyncSession
) -> None:
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(
            "You write wrong page name, please choose the page from the list"
        )
        return
    await orm_change_banner_image(
        session,
        for_page,
        image_id,
    )
    await message.answer("Banner added/changed successfully!")
    await state.clear()

@admin_router.message(AddBanner.image)
async def not_correct_add_banner(message: types.Message) -> None:
    await message.answer("You write wrong data, please load the image of the banner:")


@admin_router.callback_query(StateFilter(None), F.data.startswith("edit_"))
async def edit_product_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split("_")[-1]
    product_for_change = await orm_get_product(session, int(product_id))

    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        "Enter the name of the product you want to change:",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter(None), F.text == "Add good")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Enter the name of the product you want to add:",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter("*"), Command("cancel"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "cancel")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_data()
    if current_state is None:
        return
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
async def add_description(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        if 4 >= len(message.text) <= 1000:
            await message.answer(
                "Product description is too long or too short, \n please write the description of the product:"
            )
            return

        await state.update_data(description=message.text)

    categories = await orm_get_categories(session)
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
async def category_choice(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    if int(callback.data) in [
        category.id for category in await orm_get_categories(session)
    ]:
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
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):

    if message.text and message.text == "." and AddProduct.product_for_change:
        await state.update_data(image=AddProduct.product_for_change.image)

    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await message.answer(
            "You write wrong data, please load the image of the product:"
        )
        return

    data = await state.get_data()

    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
            await orm_add_product(session, data)
        await message.answer("Good add/change successfully!", reply_markup=ADMIN_KB)
        await state.clear()
    except Exception as e:
        await message.answer(
            f"Error: \n {e} \n Please try again or write 'cancel' to cancel the operation.'",
            reply_markup=ADMIN_KB,
        )
        await state.clear()

    AddProduct.product_for_change = None

@admin_router.message(AddProduct.image)
async def not_correct_add_image(message: types.Message, state: FSMContext):
    await message.answer("You write wrong data, please load the image of the product:")

