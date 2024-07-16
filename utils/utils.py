from string import punctuation
from typing import List, Set, Tuple
import os


def clean_text(text: str) -> str:
    return text.translate(str.maketrans('', '', punctuation))


def get_restricted_words():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    file_path = os.path.join(dir_path, '..', 'files', 'restricted_words.txt')

    with open(file_path, 'r') as file:
        restricted_words = set(word.strip() for word in file.readlines())

    return restricted_words