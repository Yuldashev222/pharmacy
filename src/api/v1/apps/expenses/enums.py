from enum import Enum


class DefaultExpenseType(Enum):
    obed = 1
    ujin = 2
    zavtrak = 3
    wi_fi = 4
    kommunal = 5
    ijaraga = 6
    oylik = 7

    @classmethod
    def choices(cls):
        return ((i.name, i.value) for i in cls)
