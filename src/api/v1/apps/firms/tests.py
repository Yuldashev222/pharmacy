# import math
#
# birlar = {
#     '1': 'bir',
#     '2': 'ikki',
#     '3': 'uch',
#     '4': 'to\'rt',
#     '5': 'besh',
#     '6': 'olti',
#     '7': 'yetti',
#     '8': 'sakkiz',
#     '9': 'to\'qqiz',
# }
#
# unlar = {
#     '1': 'o\'n',
#     '2': 'yigirma',
#     '3': 'o\'ttiz',
#     '4': 'qirq',
#     '5': 'ellik',
#     '6': 'oltmish',
#     '7': 'yetmish',
#     '8': 'sakson',
#     '9': 'to\'qson',
# }
#
# dct = {
#     '3': 'yuz',
#     '4': 'ming',
#     '7': 'million',
#     '10': 'milliard',
# }
#
# n = 123456
# digit = len(str(n))
# ten_power = int(math.pow(10, digit - 1))
# print(ten_power)
#
# while digit >= 1:
#     temp = n // ten_power
#
#     if digit % 3 == 2 or digit == 2:
