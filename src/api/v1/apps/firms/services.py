import os
import requests
from django.conf import settings


def firm_logo_upload_location(obj, logo):
    return f'firms/{obj.name[:200]}/logos/{logo}'


class EskizUz:
    ESKIZ_UZ_TOKEN = os.getenv('ESKIZ_UZ_TOKEN')

    @classmethod
    def get_token(cls):
        response = requests.request(
            method='POST',
            url=settings.ESKIZ_UZ_TOKEN_URL,
            data={'email': settings.ESKIZ_UZ_EMAIL, 'password': settings.ESKIZ_UZ_PASSWORD}
        )
        token = response.json()['data']['token']
        return token

    @classmethod
    def get_str_price(cls, price):
        return price

    @classmethod
    def success_message(cls, firm_worker_name, price):
        message = f'Hurmatli {firm_worker_name} {price} ({cls.get_str_price(price)}) \
        so\'m mablag\' olganligingiz haqida kodni tasdiqladingiz. Rahmat'
        return message

    @classmethod
    def verify_code_message(cls, firm_name, pharmacy_name, price, verify_code, firm_worker_name):
        message = f'Hurmatli {firm_worker_name} sizga tasdiqlash kodi yuborildi. Ushbu kod orqali \
        "{firm_name}" MCHJ hisobiga, "{pharmacy_name}" tomonidan {price} ({cls.get_str_price(price)}) \
        so\'m mablag\' olganligingiz to\'g\'riligini tasdiqlaysiz. Kod: {verify_code}'
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
            headers={'AUTHORIZATION': 'Bearer ' + str(cls.ESKIZ_UZ_TOKEN)},
            data=data
        )
        if response.status_code == 401:
            os.environ.setdefault('ESKIZ_UZ_TOKEN', cls.get_token())
            response = requests.request(
                method='POST',
                url=settings.ESKIZ_UZ_SEND_SMS_URL,
                headers={'AUTHORIZATION': 'Bearer ' + cls.ESKIZ_UZ_TOKEN},
                data=data
            )
        return response.status_code
