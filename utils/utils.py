import logging
import os
from string import punctuation
from typing import List, Set, Tuple


def clean_text(text: str) -> str:
    return text.translate(str.maketrans("", "", punctuation))


def get_restricted_words(file_path: str = "files/restricted_words.txt") -> Set[str]:

    try:
        with open(file_path, "r") as file:
            restricted_words = {word.strip() for word in file}
            return restricted_words
    except FileNotFoundError:
        logging.error("File not found")
        return set()
