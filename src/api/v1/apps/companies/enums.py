from enum import Enum


class StaticEnv(Enum):
    workers_id = 1
    return_product_id = 2
    discount_id = 3


class Month(Enum):
    jan = "January"
    feb = "February"
    mar = "March"
    apr = "April"
    may = "May"
    jun = "June"
    jul = "July"
    aug = "August"
    sep = "September"
    oct = "October"
    nov = "November"
    dec = "December"

    @classmethod
    def choices(cls):
        return ((i.name, i.value) for i in cls)
