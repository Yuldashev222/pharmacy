import math

dct = {
    "1": "bir ",
    "2": "ikki ",
    "3": "uch ",
    "4": "to'rt ",
    "5": "besh ",
    "6": "olti ",
    "7": "yetti ",
    "8": "sakkiz ",
    "9": "to'qqiz ",
}

dct2 = {
    "1": "o'n ",
    "2": "yigirma ",
    "3": "o'ttiz ",
    "4": "qirq ",
    "5": "ellik ",
    "6": "oltmish ",
    "7": "yetmish ",
    "8": "sakson ",
    "9": "to'qson ",
}

number = 12_132_343_241
result = ''

digit = len(str(number))
ten_power = int(math.pow(10, digit - 1))

while digit >= 1:
    temp = number // ten_power

    if digit % 3 == 2 or digit == 2:
        if str(temp) in dct2:
            result += dct2[str(temp)]
    elif str(temp) in dct:
        result += dct[str(temp)]

    if digit % 3 == 0:
        result += 'yuz '

    if digit == 4:
        result += 'ming '
    elif digit == 7:
        result += 'million '
    elif digit == 10:
        result += 'milliard '

    number %= ten_power
    ten_power //= 10
    digit -= 1

