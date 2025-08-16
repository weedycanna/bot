from decimal import Decimal
from string import punctuation
from typing import Set

from phonenumbers import (PhoneNumberFormat, format_number, is_valid_number,
                          parse)
from phonenumbers.phonenumberutil import NumberParseException

from handlers.payment import CryptoApiManager


def clean_text(text: str) -> str:
    return text.translate(str.maketrans("", "", punctuation))


def get_restricted_words(file_path: str = "files/restricted_words.txt") -> Set[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            restricted_words = {
                word.strip().lower() for line in file for word in line.split(",")
            }
            return restricted_words
    except FileNotFoundError:
        return set()


def format_phone_number(phone: str) -> str | None:
    try:
        phone_number = parse(phone, "UA")
        if not is_valid_number(phone_number):
            return None
        return format_number(phone_number, PhoneNumberFormat.INTERNATIONAL)
    except NumberParseException:
        return None


async def convert_currency(amount_usd, user_language: str) -> tuple[Decimal, str]:
    amount_usd = Decimal(amount_usd)
    if user_language == "ru":
        usd_to_rub = await CryptoApiManager.get_usd_to_rub_rate()
        usd_to_rub = Decimal(str(usd_to_rub))
        return amount_usd * usd_to_rub, "₽"
    else:
        return amount_usd, "$"


def format_price(amount: Decimal, currency: str) -> str:
    if currency == "₽":
        return f"{amount:.0f} {currency}"
    else:
        return f"{amount:.2f} {currency}"
