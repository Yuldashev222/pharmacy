from enum import Enum


class PriceType(Enum):
    t = 'Terminal'
    n = 'Naxt'
    p = 'Perevod'

    @classmethod
    def choices(cls):
        return ((i.name, i.value) for i in cls)


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
