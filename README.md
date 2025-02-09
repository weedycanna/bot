# Telegram Pizzeria Bot 🍕

This bot was created to simplify the process of ordering pizza directly through Telegram. With an intuitive interface, users can effortlessly browse the menu, place orders, and make payments, all within a single chat. The bot ensures a smooth, secure, and efficient experience for both customers and administrators. For enhanced management, the bot features an advanced admin panel accessible via Telegram and Django Admin, providing a user-friendly interface for handling orders, products, categories, and etc. PostgreSQL is used as a reliable database for securely storing user data, orders, and catalog information, ensuring data integrity and performance. Additionally, Docker is implemented for easy deployment and scalability, allowing the bot to run seamlessly across different environments.

In the bot you can find such functions:
   - Viewing the catalog with convenient navigation and pagination
   - Payment via Telegram Pay and cryptocurrency payments
   - Placing orders and viewing order details
   - Subscription check before using the bot
   - User registration and profile with order history
   - Sending notifications and messages to users
   - Sales and activity statistics
   - Admin panel in Telegram and Django Admin
   - CRUD operations for managing products, categories, and banners
   - Captcha for spam protection

#### Stack:

- [Python](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/)
- [Aiogram](https://docs.aiogram.dev/en/latest/)
- [Docker](https://www.docker.com/)
- [Django](https://www.djangoproject.com/)

## Local Developing

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

## Docker 

   ```bash
   docker build .

   docker-compose up
   ```
   
## Run application

```
Example env values

TOKEN=7765659692:AAG0gyOcBtuFiu2Ab1-9P0YYg0KtYy-tYEW
DB_PG=postgresql+asyncpg://test:tests@localhost:5432/test
CRYPTO_TOKEN=17965:AA83cK37am3814tjP8R50mqFiy5EgRQYzca
STAR_PAYMENT_TOKEN=439694247:TEST:21a24e76-d547-4cbd-bdba-2a98f9aa474e

Run a file called app.
```

## License

This project uses the [MIT] license(https://github.com/Sauberr/pizzeria-bot/blob/master/LICENSE)

## Contact 

To contact the author of the project, write to email 𝚍𝚖𝚒𝚝𝚛𝚒𝚢𝚋𝚒𝚛𝚒𝚕𝚔𝚘@𝚐𝚖𝚊𝚒𝚕.𝚌𝚘𝚖.
