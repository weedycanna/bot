import math
from typing import List, Set, Tuple

# Pagination class


class Paginator:
    def __init__(self, array: List | Tuple, page: int = 1, per_page: int = 1):
        self.array = array
        self.page = page
        self.per_page = per_page
        self.len = len(self.array)

        self.pages = math.ceil(self.len / self.per_page)

    def __get_slice(self):
        start = (self.page - 1) * self.per_page
        stop = start + self.per_page
        return self.array[start:stop]

    def get_page(self):
        page_items = self.__get_slice()
        return page_items

    def has_next(self):
        if self.page < self.pages:
            return self.page + 1
        return False

    def has_previous(self):
        if self.page > 1:
            return self.page - 1
        return False

    def get_next(self):
        if self.page < self.pages:
            self.page += 1
            return self.get_page()
        raise IndexError('Next page does not exist. Use has_next() to check if there is a next page')

    def get_previous(self):
        if self.page > 1:
            self.page -= 1
            return self.__get_slice()
        raise IndexError('Previous page does not exist. Use has_previous() to check if there is a previous page')
