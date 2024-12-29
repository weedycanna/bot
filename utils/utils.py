from string import punctuation
from typing import Set

from aiogram.utils.formatting import PhoneNumber
from phonenumbers import PhoneNumberFormat, format_number, is_valid_number, parse


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


def format_phone_number(phone: str) -> str:
    try:
        phone_number = parse(phone, "UA")
        if not is_valid_number(phone_number):
            return None
        return format_number(phone_number, PhoneNumberFormat.INTERNATIONAL)
    except PhoneNumber:
        return None
