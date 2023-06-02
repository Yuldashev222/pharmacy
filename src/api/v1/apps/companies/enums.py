from enum import Enum


class DefaultTransferType(Enum):
    cash = 1
    payme = 2
    click = 3
    pharmacy_account = 4
    account = 4
    uz_card = 5
    orange = 6
    grape = 7
    xumo = 8

    @classmethod
    def choices(cls):
        return ((i.name, i.value) for i in cls)
