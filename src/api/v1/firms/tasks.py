from celery import shared_task
from datetime import timedelta, date
from time import sleep

from .models import FirmIncome
from .services import EskizUz


@shared_task
def send_sms_to_director():
    incomes = FirmIncome.objects.filter(deadline_date__isnull=False, is_paid=False).select_related('from_firm',
                                                                                                   'from_firm__director')
    today_date = date.today()

    for income in incomes:
        if income.deadline_date - timedelta(days=3) == today_date:
            message = f'Eslatma: "{income.from_firm.send_sms_name}" tomonidan ' \
                      f'{income.report_date} kuni olingan ' \
                      f'{income.price} so\'m tovardan qarzingiz ' \
                      f'{income.remaining_debt} so\'m qoldi. ' \
                      f'Qarzni to\'liq qaytarish muddatiga 3 kun qoldi.'

            EskizUz.send_sms(phone_number=income.from_firm.director.phone_number[1:], message=message)
            sleep(2)
