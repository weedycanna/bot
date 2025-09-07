# --- General & Welcome ---
welcome_message =
    🙌 Hello, glad to see you 🙌

    This bot will help you access the menu of our pizzeria 🍕
    You can also place an order and get information about us 📋

    All this and more will be available after registration 🔽✅

    Write your username first, and then follow the instructions

# --- Language ---
select_language = 🌐 Please select your language:
language_selected = 🇺🇸 Language changed to English

# --- Navigation Buttons ---
back_button = ⬅️ Back
next_button = Next ▶
prev_button = ◀ Prev
main_menu_button = Main 🏠

# --- Main Menu ---
main_menu_goods = Goods 🍕
main_menu_cart = Cart 🛒
main_menu_orders = Orders 📦
main_menu_about = About us ℹ️
main_menu_payment = Payment 💰
main_menu_delivery = Delivery 🚚
main_menu_profile = Profile 👤
main_menu_language = Language 🌐

# --- Subscription ---
subscription_required = 🚫 Please subscribe to the channels to use the bot:
    [Subscribe to the channel]({$channel_link})
check_subscription_button = 🔄 Check subscription
subscription_successful = ✅ You have successfully subscribed to the channel!
subscription_required_callback = ❌ You are not subscribed to the channel. Please subscribe first.

subscribe_to_channel_button = ✅ Subscribe to Channel

# --- Captcha ---
captcha_text =
    Hello! Before we begin, please confirm that you are not a robot. Select the specified word: <strong>{$word}</strong>
    <i>After passing the captcha, you can proceed with registration</i>
captcha_success = Captcha passed successfully!
captcha_expired = Captcha session expired. Please start again.
captcha_wrong_selection = Wrong selection. Try again with a new captcha.
captcha_passed = ✅ Passed
captcha_not_passed = ❌ Not passed
complete_captcha_first = Please complete the captcha first.

# --- Registration ---
first_name_request = Please enter your name:
name_length_error = Name must be between 2 and 50 characters. Please enter your name again:
name_too_long = ❌ The name is too long. Please enter a name shorter than 30 characters.
phone_request =
    Now, please enter your phone number
    📱 The phone number format should be +7xxxxxxxxxx
    ⚠️ Attention! The phone number must be unique
invalid_phone_format =
    ❌ Invalid phone number format. Please enter the number in international format
    Examples:
    +380 XX XXX XXXX
    +7 XXX XXX XXXX
invalid_phone_format_intl = ❌ Invalid phone number format. Please enter the number in international format (for example, +79123456789):
invalid_phone_retry = ❌ Invalid phone number format. Please try again.
phone_already_registered = ❌ This phone number is already registered with another account. Please use a different phone number or contact the administrator.
registration_complete_with_data =
    ✅ Registration completed successfully!
    Name: {$name}
    Phone: {$phone}
user_creation_error = Error creating user. Please try again.
registration_error = ❌ An error occurred during registration. Please try again later.

# --- User Profile ---
profile_text =
    <b>⚡️ Profile</b>
    👉🏼 ID: <code>{$user_id}</code>
    ➖➖➖➖➖➖➖➖➖➖➖➖
    ⚙️ Fullname: <code>{$first_name} {$last_name}</code>
    🎮 Username: <code>@{$username}</code>
    📱 Phone: <code>{$phone}</code>
    🔐 Captcha: <code>{$captcha_status}</code>
    🚩 Language: <code>{$language}</code>
    ➖➖➖➖➖➖➖➖➖➖➖➖
    📊 Statistics:
    📅 Days in bot: <code>{$days_in_bot}</code>
    📦 Total orders: <code>{$orders_count}</code>
    ➖➖➖➖➖➖➖➖➖➖➖➖
    📆 Registration date: <code>{$registration_date}</code>
profile_load_error = An error occurred while loading the profile

# --- Catalog & Products ---
select_category = Select a category:
categories_not_found = Categories not found
product_details =
    <strong>{$name}</strong>
    {$description}
    Price: {$price}
    <strong>Good {$current_page} of {$total_pages}</strong>
product_no_image = Product has no image
menu_banner_with_image =
    <b>{$description}</b>
    Select a category:

# --- Cart ---
cart_button = Cart 🛒
buy_button = Buy 💵
delete_button = Delete
product_added_to_cart = Product added to cart.
error_adding_to_cart = Error adding product to cart.
cart_item_details =
    <strong>{$name}</strong>
    {$price}$ x {$quantity} = {$cart_price}$
    Good {$current_page} of {$total_pages} in cart.
    Total price in cart {$total_price}

# --- Ordering Process ---
order_button = Order 🛍️
name_request_again = Please enter your name again:
phone_request_order = Please enter your phone number:
phone_request_again = Please enter your phone number again:
invalid_phone_format_order = Invalid phone number. Please enter a valid phone number (10-15 digits):
phone_accepted_address_request = Phone number accepted. Please enter your address:
address_request_again = Please enter your address again:
address_length_error = ❌ Address must be between 5 and 100 characters. Please enter your address again:
order_confirmation =
    <b>📋 Order Details</b>
    <i>👤 Customer Information:</i>
        • Name: <code>{$name}</code>
        • Phone: <code>{$phone}</code>
        • Address: <code>{$address}</code>
    <i>💰 Payment Information:</i>
        • Total Amount: <b>${$total_amount}</b>
    <i>⬇️ Please select payment method below</i>
select_payment_btn = Select Payment Method 💳
cancel_order_btn = Cancel ❌
user_agreement_btn = User agreement 📜
order_canceled = Order canceled ❌

# --- Payment ---
select_payment_method = <b>💳 Select Payment Method:</b>
pay_with_crypto_btn = Pay with {$crypto} 💳
pay_with_stars_btn = Pay {$stars_amount} Stars ⭐
star_payment_btn = Star Payment ⭐
order_payment_title = Order Payment
order_payment_description = Order payment for user ID: {$user_id}
star_payment_description = Payment for the amount {$stars_amount} Stars
payment_details =
    <b>📋 Payment Details</b>
    <i>💰 Payment Information:</i>
        • Amount USD: <b>${$amount_usd}</b>
        • Amount {$crypto}: <b>{$crypto_amount}</b>
        • Currency: <b>{$crypto}</b>
        • Expiration: <code>{$expiration_time}</code>
    <i>⏰ Time Remaining: 3 minutes</i>
    <b>ℹ️ Please complete the payment before the timer expires</b>
payment_successful =
    <b>Payment Successful</b>
    <i>Order Information:</i>
        • Order ID: <code>{$order_id}</code>
        • Status: <b>{$order_status}</b>
    <i>Payment Details:</i>
        • Amount: <b>${$amount}</b>
        • Currency: <b>{$crypto}</b>
    <i>Delivery Information:</i>
        • Name: <code>{$name}</code>
        • Phone: <code>{$phone}</code>
        • Address: <code>{$address}</code>
    <i>You can view your order details in the Orders menu</i>
payment_time_expired =
    <b>⏰ Payment Time Expired!</b>
    ❌ The payment was not completed within the allowed time.
    Please try again if you wish to complete the purchase.

# --- Order History ---
no_orders = You have no orders yet.
order_item =
    🔸 Order {$order_id}
    👤 Name: {$name}
    📦 Status: {$status}
    📍 Address: {$address}
    📱 Phone: <code>{$phone}</code>
    -------------------

order_detail_button = 📋 Order detail #{$order_id}
back_to_orders_btn = ◀️ Back to orders


order_detail_header =
    📋 <b>Order Details #{$order_id}</b>
    📅 Created at: {$created_at}
    👤 Name: {$name}
    📦 Status: {$status}
    📍 Address: {$address}
    📱 Phone: <code>{$phone}</code>

    <b>Items in your order:</b>

order_detail_item =
    • <b>{$name}</b>
      <i>{$quantity} pcs x ${$price}</i>

order_detail_total =
    -----------------------------------
    💰 <b>Total cost: ${$total_sum}</b>


back-to-orders-btn = ◀️ Back to orders

# --- System Errors & Messages ---
unrecognized_action = Unrecognized action.
error_loading_menu = Error loading menu
error_opening_menu = Error opening menu {$menu_name}
banner_not_found = Banner not found
banner_no_image = Banner has no image
banner_image_not_found = Banner image not found: {$path}
banner_not_found_or_no_image = Banner not found or has no image
product_image_not_found = Product image not found: {$path}
order_details_error = There was an error retrieving order details
order_not_found = Order not found
order_no_products = The order has no products
order_already_processed = This order has already been processed!
captcha_save_error = Error saving captcha status. Please try again.
captcha_general_error = An error occurred. Please try again.
crypto_rate_error = ❌ Error getting exchange rate. Please try again.
crypto_calculation_error = ❌ Error calculating crypto amount. Please try again.
crypto_invoice_error = ❌ Error creating crypto invoice. Please try again.
invalid_payment_response = ❌ Invalid payment response. Please try again.
payment_data_save_error = ❌ Error saving payment data. Please try again.
payment_details_display_error = ❌ Error displaying payment details. Please try again.
payment_processing_error = ❌ Payment processing error. Please try again or contact support.
star_payment_error = Error processing Star payment
payment_received_order_failed =
    ❌ <b>Payment received but order creation failed.</b>
    Please contact support.

# --- Admin Panel ---
admin_no_access = ❌ You do not have sufficient rights to access this feature.
admin_kb_placeholder = What do you want to do?
admin_add_good = ➕ Add good
admin_assortment = 🛒 Assortment
admin_add_banner = 🖼️ Add/Change banner
admin_statistics = 📊 Statistics
admin_newsletter = 📣 Newsletter
admin_statistics_text =
    📊 Statistics:
    👥 Total users: {$users}
    🛒 Total orders: {$orders}
    📦 Total products: {$products}
    📂 Products by Category:
     {$category_stats_text}
admin_products_list = Ok, list of products ⏫
admin_choose_category = Choose the category:
admin_product_card =
    <strong>{$name}</strong>
    {$description}
    Price: {$price}💵
admin_delete_btn = Delete
admin_edit_btn = Edit
admin_product_deleted = Good deleted successfully!
admin_banner_instructions =
    Send a banner photo.
    Choose the page for the banner:
    {$pages}
admin_banner_wrong_page = You write wrong page name, please choose the page from the list
admin_banner_success = Banner added/changed successfully!
admin_product_add_en_name = Enter the name of the product in en you want to add:
admin_product_add_ru_name = Enter the name of the product in ru you want to add:
admin_product_edit_name = Enter the name of the product you want to change:
admin_product_add_en_description = Enter the description of the product in en:
admin_product_add_ru_description = Enter the description of the product in ru:
admin_product_price = Enter the price of the product:
admin_product_image = Load the image of the product:
admin_image_keep_current = Send a photo or '.' to keep the current image
admin_product_success = Product added/updated successfully!
admin_canceled = Canceled
admin_no_previous_step = Previous step is not available, or write "cancel"
admin_previous_step =
    Ok, you are on the previous step
    {$step_text}
admin_newsletter_content = Enter the content of the newsletter
admin_newsletter_success =
    <b> 🎉 Newsletter sent successfully!
    ✅ Sent to: {$success_count}
    ❌ Errors occurred while sending: {$error_count}
    ⏳ Time taken: <code>{$time_taken} sec.</code></b>

# --- Admin Errors ---
admin_products_error = Error occurred while processing products
admin_banner_wrong_data = You write wrong data, please load the image of the banner:
admin_product_name_error = Product name is too long or too short, please write the name of the product:
admin_product_name_wrong_data = You write wrong data, please write the name of the product:
admin_product_description_error =
    Product description is too long or too short,
    please write the description of the product:
admin_product_description_wrong_data = You write wrong data, please write the description of the product:
admin_category_wrong_choice = Choose the category from the list
admin_category_wrong_data = You write wrong data, please choose the category from the list:
admin_price_error = Write correct data, digit only
admin_product_price_wrong_data = You write wrong data, please write the price of the product:
admin_product_image_wrong_data = You write wrong data, please load the image of the product:
admin_product_error = Error occurred. Try again or type 'cancel'

# --- Group Management (Admin) ---
messages_deleted = Deleted {$count} messages!
invalid_clear_format = Invalid command format. Use: /clear or /clear <number>
clear_admin_only = The command is only available to group administrators.
bot_admin_required = Bot must be a group admin to delete messages
clear_command_format = Invalid command format. Use: /clear <number>
restricted_words_warning = {$user_name}, keeps order in the chat! 🤬