from aiogram.utils.formatting import Bold, as_list, as_marked_section

categories = ["Food", "Beverages"]


description_for_info_pages = {
    "main": "Welcome to our ChilliPizza!",
    "about": "We are a small pizza with a large selection of products.",
    "payment": as_marked_section(
        Bold("Payment Options:"),
        "Card in Bot",
        "Cash/Cart Payment",
        "Cryptocurrency Payment",
        marker="✅ ",
    ).as_html(),
    "shipping": as_list(
        as_marked_section(
            Bold("Delivery Options:"), "Pickup", "Courier", "Post", marker="✅ "
        ),
        as_marked_section(Bold("Cancel:"), "Pigeons", "Teleport", marker="❌ "),
        sep="\n----------------\n",
    ).as_html(),
    "catalog": "Categories: ",
    "cart": "Cart empty!",
}
