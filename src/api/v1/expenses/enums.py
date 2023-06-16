from enum import Enum


class DefaultExpenseType(Enum):
    worker = 1
    return_product_id = 2
    discount_id = 3

    @classmethod
    def choices(cls):
        return ((i.name, i.value) for i in cls)
