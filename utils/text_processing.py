from string import punctuation
from typing import Set


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
