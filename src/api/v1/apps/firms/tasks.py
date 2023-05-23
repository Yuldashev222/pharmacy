from celery import shared_task
from datetime import timedelta, date

from api.v1.apps.accounts.models import CustomUser

from .models import FirmIncome
from .services import EskizUz


@shared_task
def send_sms_to_director():
    incomes = FirmIncome.objects.filter(deadline_date__isnull=False, is_paid=False)
    today_date = date.today()
    for income in incomes:
        if income.deadline_date - timedelta(days=1) == today_date:
            director = CustomUser.objects.get(id=income.creator.director_id)
            firm_name = ' '.join([i for i in str(income.from_firm) if i.isalpha()])

            message = f'Eslatma: "{firm_name}" MCHJ tomonidan ' \
                      f'{income.created_at.strftime("%d.%m.%Y")} kuni olingan ' \
                      f'{income.price} so\'m tovardan qarzingiz ' \
                      f'{income.price - income.remaining_debt} so\'m qoldi. ' \
                      f'Qarzni to\'liq qaytarish muddatiga 3 kun qoldi.'
            EskizUz.send_sms(phone_number=director.phone_number, message=message)
