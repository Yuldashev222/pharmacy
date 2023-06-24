from celery import shared_task
from django.db.models import Sum

from . import models


@shared_task
def update_all_next_remainders(pharmacy_id, report_date, shift):
    objs1 = models.RemainderShift.objects.filter(pharmacy_id=pharmacy_id, shift__gt=shift, report_date=report_date)
    objs2 = models.RemainderShift.objects.filter(pharmacy_id=pharmacy_id, report_date__gt=report_date)

    objs = objs1 | objs2
    objs = objs.order_by('-report_date')

    for obj in objs:
        price = models.RemainderDetail.objects.filter(pharmacy_id=obj.pharmacy_id,
                                                      report_date=obj.report_date,
                                                      shift__lte=obj.shift
                                                      ).aggregate(s=Sum('price'))['s']
        price = price if price else 0

        price2 = models.RemainderDetail.objects.filter(pharmacy_id=obj.pharmacy_id,
                                                       report_date__lt=obj.report_date,
                                                       ).aggregate(s=Sum('price'))['s']
        price += price2 if price2 else 0

        obj.price = price
        obj.save()
