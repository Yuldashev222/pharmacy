import math
import requests
from django.db import models
from django.conf import settings


def firm_logo_upload_location(obj, logo):
    return f'firms/{obj.name[:200]}/logos/{logo}'


class EskizUzToken(models.Model):
    token = models.TextField()


class EskizUz:

    @classmethod
    def get_token(cls):
        token = EskizUzToken.objects.all()
        if token.exists():
            return token.first().token
        response = requests.request(
            method='POST',
            url=settings.ESKIZ_UZ_TOKEN_URL,
            data={'email': settings.ESKIZ_UZ_EMAIL, 'password': settings.ESKIZ_UZ_PASSWORD}
        )
        token = response.json()['data']['token']
        EskizUzToken.objects.create(token=token)
        return token

    @classmethod
    def get_str_price(cls, price):
        birlar = {
            1: 'bir ',
            2: 'ikki ',
            3: 'uch ',
            4: 'to\'rt ',
            5: 'besh ',
            6: 'olti ',
            7: 'yetti ',
            8: 'sakkiz ',
            9: 'to\'qqiz ',
        }
        unlar = {
            1: 'o\'n ',
            2: 'yigirma ',
            3: 'o\'ttiz ',
            4: 'qirq ',
            5: 'ellik ',
            6: 'oltmish ',
            7: 'yetmish ',
            8: 'sakson ',
            9: 'to\'qson ',
        }
        dct = {
            4: 'ming ',
            7: 'million ',
            10: 'milliard ',
        }

        digit = len(str(price))
        ten_power = int(math.pow(10, digit - 1))
        result = ''
        while digit >= 1:
            temp = price // ten_power

            if digit % 3 == 2 or digit == 2:
                if temp in unlar:
                    result += unlar[temp]
            elif temp in birlar:
                result += birlar[temp]

            if digit % 3 == 0 and temp != 0:
                result += 'yuz '

            if not (
                    result.endswith('milliard ') or result.endswith('million ') or result.endswith('ming ')
            ) and digit in dct:
                result += dct[digit]

            price %= ten_power
            ten_power //= 10
            digit -= 1

        return result.strip()

    @classmethod
    def success_message(cls, firm_worker_name, price):
        message = f'Hurmatli {firm_worker_name} {price} ({cls.get_str_price(price)}) ' \
                  f'so\'m mablag\' olganligingiz haqida kodni tasdiqladingiz. Rahmat'
        return message

    @classmethod
    def return_product_success_message(cls, firm_worker_name, price):
        message = f'Hurmatli {firm_worker_name} {price} ({cls.get_str_price(price)}) ' \
                  f'so\'m miqdoridagi mahsulotlarni qaytarib olganligingiz haqida kodni tasdiqladingiz: Rahmat'
        return message

    @classmethod
    def verify_code_message(cls, firm_name, pharmacy_name, price, verify_code, firm_worker_name):
        message = f'Hurmatli {firm_worker_name} sizga tasdiqlash kodi yuborildi. ' \
                  f'Ushbu kod orqali "{firm_name}" MCHJ hisobiga, "{pharmacy_name}" ' \
                  f'tomonidan {price} ({cls.get_str_price(price)}) so\'m mablag\' ' \
                  f'olganligingiz to\'g\'riligini tasdiqlaysiz. Kod: {verify_code}'
        return message

    @classmethod
    def return_product_verify_code_message(cls, firm_name, price, verify_code, firm_worker_name, company_name):
        message = f'Hurmatli {firm_worker_name} sizga tasdiqlash kodi yuborildi. ' \
                  f'Ushbu kod orqali "{firm_name}" MCHJ hisobiga, "{company_name}" ' \
                  f'tomonidan {price} ({cls.get_str_price(price)}) so\'m miqdoridagi mahsulotlarni qaytarib ' \
                  f'olganligingiz to\'g\'riligini tasdiqlaysiz. Kod: {verify_code}'
        return message

    @classmethod
    def send_sms(cls, phone_number, message):
        data = {
            'mobile_phone': phone_number,
            'message': message,
            'from': settings.ESKIZ_UZ_ALPHA_NICK,
            'callback_url': settings.ESKIZ_UZ_CALLBACK_URL,
        }
        response = requests.request(
            method='POST',
            url=settings.ESKIZ_UZ_SEND_SMS_URL,
            headers={'AUTHORIZATION': 'Bearer ' + cls.get_token()},
            data=data
        )
        if response.status_code == 401:
            EskizUzToken.objects.all().delete()
            response = requests.request(
                method='POST',
                url=settings.ESKIZ_UZ_SEND_SMS_URL,
                headers={'AUTHORIZATION': 'Bearer ' + cls.get_token()},
                data=data
            )
        return response.text
