from time import sleep
from celery import shared_task
from datetime import date

from api.v1.firms.services import EskizUz

from .models import Client


@shared_task
def send_sms_to_client():
    today_date = date.today()
    clients = Client.objects.filter(director__is_active=True, birthdate__isnull=False)

    for client in clients:
        if client.birthdate == today_date:
            message = 'Hello'
            EskizUz.send_sms(phone_number=client.phone_number1[1:], message=message)
            sleep(1)
