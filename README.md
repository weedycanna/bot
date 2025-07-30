<h1 align="center"> 🍕 Telegram Pizzeria Bot 🍕 </h1>

</br>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Aiogram-3.0+-red?style=for-the-badge&logo=telegram&logoColor=white">
  </br>
  <img src="https://img.shields.io/badge/PostgreSQL-13+-blue?style=for-the-badge&logo=postgresql&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker&logoColor=white">
  </br>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge">
  </br>
</p>

<h1 align="left"> 📋 About</h1> 

</br>

This bot was created to simplify the process of ordering pizza directly through Telegram. With an intuitive interface, users can effortlessly browse the menu, place orders, and make payments, all within a single chat. The bot ensures a smooth, secure, and efficient experience for both customers and administrators. For enhanced management, the bot features an advanced admin panel accessible via Telegram and Django Admin, providing a user-friendly interface for handling orders, products, categories, and etc. PostgreSQL is used as a reliable database for securely storing user data, orders, and catalog information, ensuring data integrity and performance. Additionally, Docker is implemented for easy deployment and scalability, allowing the bot to run seamlessly across different environments.

## Stack:

 - **Backend**: [**`Python 3.12+`**](https://python.org/)
 - **Framework**: [**`Aiogram 3.0+`**](https://docs.aiogram.dev/)
 - **Database**: [**`PostgreSQL`**](https://postgresql.org/)
 - **Admin Panel**: [**`Django`**](https://djangoproject.com/)
 - **Deployment**: [**`Docker`**](https://docker.com/)


<table align="center">
  <tr>
    <td align="center" width="50%">
      <b>📱 Main Menu</b><br/>
      <img src="demonstration/1.png" width="300px" alt="Main Menu"/>
    </td>
    <td align="center" width="50%">
      <b>🔒 Captcha Protection</b><br/>
      <img src="demonstration/2.png" width="300px" alt="Captcha"/>
    </td>
  </tr>
  <tr>
    <td align="center">
      <b>🛒 Product Catalog</b><br/>
      <img src="demonstration/3.png" width="300px" alt="Catalog"/>
    </td>
    <td align="center">
      <b>👤 User Profile</b><br/>
      <img src="demonstration/4.png" width="300px" alt="Profile"/>
    </td>
  </tr>
  <tr>
    <td align="center">
      <b>🛍️ Product Details</b><br/>
      <img src="demonstration/5.png" width="300px" alt="Product Cart"/>
    </td>
    <td align="center">
      <b>🛒 Shopping Cart</b><br/>
      <img src="demonstration/6.png" width="300px" alt="Cart"/>
    </td>
  </tr>
  <tr>
    <td align="center">
      <b>💳 Payment System</b><br/>
      <img src="demonstration/7.png" width="300px" alt="Payment"/>
    </td>
    <td align="center">
      <b>📦 Order History</b><br/>
      <img src="demonstration/8.png" width="300px" alt="Orders"/>
    </td>
  </tr>
  <tr>
    <td align="center">
      <b>📋 Order Details</b><br/>
      <img src="demonstration/9.png" width="300px" alt="Order Details"/>
    </td>
    <td align="center">
      <b>👨‍💼 Admin Panel (Telegram)</b><br/>
      <img src="demonstration/10.png" width="300px" alt="Admin Telegram"/>
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <b>🖥️ Admin Panel (Django)</b><br/>
      <img src="demonstration/11.png" width="600px" alt="Admin Django"/>
    </td>
  </tr>
</table>

## 🚀 Features
* Viewing the catalog with convenient navigation and pagination
* Payment via Telegram Pay and cryptocurrency payments
* Placing orders and viewing order details
* Subscription check before using the bot
* User registration and profile with order history
* Sending notifications and messages to users
* Sales and activity statistics
* Admin panel in Telegram and Django Admin
* CRUD operations for managing products, categories, and banners
* Captcha for spam protection
* Localization


## 🛠️ Local Developing
All actions should be executed from the source directory of the project and only after installing all requirements.

1. Firstly, create and activate a new virtual environment:
   ```bash
   python3.12 -m venv ../venv
   source ../venv/bin/activate
   ```
   
2. Install packages:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   
3. Install database:
   ```
   For production Postgresql
   For local Sqlite3
   ```

## 🐳 Docker 
   ```bash
   docker build .
   docker-compose up
   ```
   
## 🚀 Run application
```
Example env values
TOKEN=7765659692:AAG0gyOcBtuFiu2Ab1-9P0YYg0KtYy-tYEW
DB_PG=postgresql+asyncpg://test:tests@localhost:5432/test
CRYPTO_TOKEN=17965:AA83cK37am3814tjP8R50mqFiy5EgRQYzca
STAR_PAYMENT_TOKEN=439694247:TEST:21a24e76-d547-4cbd-bdba-2a98f9aa474e
Run a file called app.
```

## 💻 HotKeys
* **Start** - `/start`
* **Main menu** - `/menu`
* **About** - `/about`
* **User Profile** - `/profile`
* **Payment** - `/payment`
* **Orders** - `/orders`
* **Shipping** - `/shipping`
* **Admin Panel** - `/admin` (admin only)

## 📞 Contact 
To contact the author of the project, write to email dmitriybirilko@gmail.com
