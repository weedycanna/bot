from string import punctuation
from typing import Set


def clean_text(text: str) -> str:
    return text.translate(str.maketrans('', '', punctuation))


def get_restricted_words() -> Set[str]:
    with open('files/restricted_words.txt', 'r') as file:
        return set(word.strip() for word in file.read().split(','))
