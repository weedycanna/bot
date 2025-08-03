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

### 📱 Main Menu

<div align="center">
<img src="demonstration/1.png" width="800" alt="Main Menu">

### 🛒 Catalog & Ordering  
<img src="demonstration/3.png" width="800" alt="Catalog">
<img src="demonstration/5.png" width="800" alt="Product Cart">
<img src="demonstration/8.png" width="800" alt="Orders">
<img src="demonstration/9.png" width="800" alt="Order Details">

### 👨‍💼 Admin Panel via Telegram or Django
<img src="demonstration/10.png" width="800" alt="Admin Panel Telegram">
<img src="demonstration/11.png" width="800" alt="Admin Panel Django">

### 🔒 Captcha Protection
<img src="demonstration/2.png" width="800" alt="Captcha">

### 👤 User Profile
<img src="demonstration/4.png" width="800" alt="Profile">

### 💳 Payment System
<img src="demonstration/7.png" width="800" alt="Payment">

### 🛒 Cart
<img src="demonstration/6.png" width="800" alt="Cart">
</div>

## 🚀 Features

### 👨‍💼 For Administrators
* Advanced admin panel accessible via Telegram and Django Admin
* CRUD operations for managing products, categories, and banners
* Sales and activity statistics with detailed analytics
* User management and order monitoring
* Sending notifications and messages to users
* Order status management and processing
* Product inventory control

### 👤 For Users
* Intuitive catalog browsing with navigation and pagination
* Payment via Telegram Pay and cryptocurrency payments
* Easy order placement and order history viewing
* User profile with personal information and preferences
* Shopping cart functionality with quantity management
* Real-time order tracking and notifications
* Captcha protection for security
* Localization support for multiple languages
* Subscription verification before bot usage

## 🛠️ Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/telegram-pizzeria-bot.git
   cd telegram-pizzeria-bot
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3.12 -m venv ../venv
   source ../venv/bin/activate
   ```
   
3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Open `.env` file and fill in all required environment variables:
   
   ```env
   # Bot Configuration
   TOKEN=your_telegram_bot_token_here
   
   # Database Configuration
   DB_PG=postgresql+asyncpg://username:password@localhost:5432/database_name
   
   # Payment Configuration
   CRYPTO_TOKEN=your_crypto_payment_token_here
   STAR_PAYMENT_TOKEN=your_star_payment_token_here
   
   # Other required variables...
   ```

   **Where to get tokens:**
   - **Telegram Bot Token**: Create a bot via [@BotFather](https://t.me/botfather)
   - **Crypto Payment Token**: Get from your cryptocurrency payment provider
   - **Star Payment Token**: Get from Telegram Bot API documentation

5. **Set up database:**
   ```
   For production: PostgreSQL
   For local development: SQLite3
   ```

6. **Create Django superuser:**
   ```bash
   cd src
   python manage.py createsuperuser
   ```

7. **Run the application:**
   ```bash
   python app.py
   ```

## 🐳 Docker Deployment

### Quick Start
```bash
docker build .
docker-compose up -d
```

### View logs
```bash
docker-compose logs -f
```

### Create superuser via Docker
```bash
docker-compose exec web python src/manage.py createsuperuser
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
