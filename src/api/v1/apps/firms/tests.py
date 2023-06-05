from datetime import date, timedelta
from api.v1.apps.firms.models import FirmIncome, Firm


def f():
    from_firm_id = Firm.objects.last().id
    deadline_date = date.today() + timedelta(days=20)
    report_date = date.today()
    price = 2101212332
    second_name = 'testtesttestsetestsetestsetestestesttesttestsetes' \
                  'tsetestsetestestesttesttestsetestsetestsetesteste' \
                  'sttesttestsetestsetestsetestes'

    objs = []
    for i in range(500):
        objs.append(FirmIncome(from_firm_id=from_firm_id,
                               deadline_date=deadline_date,
                               report_date=report_date,
                               price=price,
                               second_name=second_name,
                               remaining_debt=price))
        deadline_date += timedelta(days=10)
        report_date += timedelta(days=3)
        price = price + i ** 2
    return FirmIncome.objects.bulk_create(objs)
