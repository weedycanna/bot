from aiogram.fsm.state import StatesGroup, State


class AddProduct(StatesGroup):
    name: str = State()
    description: str = State()
    category: str = State()
    price: float = State()
    image = State()

    product_for_change = None

    texts = {
        "AddProduct:name": "Enter the name of the product you want to add again:",
        "AddProduct:description": "Enter the description of the product again:",
        "AddProduct:category": "Enter the category of the product again:",
        "AddProduct:price": "Enter the price of the product again:",
        "AddProduct:image": "Load the image of the product again:",
    }