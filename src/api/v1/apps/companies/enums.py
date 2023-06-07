from enum import Enum


class DefaultTransferType(Enum):
    cash = 1
    payme = 2
    click = 3
    pharmacy_account = 4
    uz_card = 5
    orange = 6
    grape = 7
    xumo = 8

    @classmethod
    def choices(cls):
        return ((i.name, i.value) for i in cls)


MONTHS = {
    1: 'Yanvar',
    2: 'Fevral',
    3: 'Mart',
    4: 'Aprel',
    5: 'May',
    6: 'Iyun',
    7: 'Iyul',
    8: 'Avgust',
    9: 'Sentabr',
    10: 'Oktabr',
    11: 'Noyabr',
    12: 'Dekabr',
}
