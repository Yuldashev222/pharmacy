from celery import shared_task
from datetime import timedelta, date

from api.v1.apps.accounts.models import CustomUser

from .models import FirmIncome
from .services import EskizUz


@shared_task
def send_sms_to_director():
    print('Hello ----------------------------')
    print('Hello ++++++++++++++++++++++++++++')
    incomes = FirmIncome.objects.filter(deadline_date__isnull=False, is_paid=False)
    today_date = date.today()
    for income in incomes:
        if income.deadline_date - timedelta(days=1) == today_date:
            director = CustomUser.objects.get(id=income.creator.director_id)
            message = f'Hurmatli {str(director)} "{str(income.to_pharmacy)}" "{str(income.from_firm)}" ' \
                      f'{income.remaining_debt} ({EskizUz.get_str_price(income.remaining_debt)})'
            EskizUz.send_sms(phone_number=director.phone_number, message=message)
