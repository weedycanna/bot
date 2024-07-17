import os
from string import punctuation
from typing import List, Set, Tuple
import logging


def clean_text(text: str) -> str:
    return text.translate(str.maketrans('', '', punctuation))


def get_restricted_words() -> Set[str]:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    file_path = os.path.join(dir_path, '..', 'files', 'restricted_words.txt')

    try:
        with open(file_path, 'r') as file:
            restricted_words = {word.strip() for word in file}
            return restricted_words
    except FileNotFoundError:
        logging.error('File not found')
        return set()
