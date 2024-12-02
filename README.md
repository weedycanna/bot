# Pizzeria bot
The project for study Aiogram v3.

#### Stack:

- [Python](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/)
- [Aiogram](https://docs.aiogram.dev/en/latest/)

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
   
## Run application

```
Example env values

TOKEN=7765659692:AAG0gyOcBtuFiu2Ab1-9P0YYg0KtYy-tYEW
DB_PG=postgresql+asyncpg://test:tests@localhost:5432/test

Run a file called app.
```
