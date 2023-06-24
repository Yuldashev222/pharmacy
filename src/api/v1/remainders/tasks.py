from celery import shared_task
from django.db.models import Sum

from . import models


@shared_task
def update_all_next_remainders(pharmacy_id, report_date, shift):
    try:
        obj = models.RemainderShift.objects.get(pharmacy_id=pharmacy_id, report_date=report_date, shift=shift)
        old_obj_price = obj.price
    except models.RemainderDetail.DoesNotExist:
        old_obj_price = 0
    objs1 = models.RemainderShift.objects.filter(pharmacy_id=pharmacy_id, shift__gt=shift, report_date=report_date)
    objs2 = models.RemainderShift.objects.filter(pharmacy_id=pharmacy_id, report_date__gt=report_date)

    objs = objs1 | objs2
    objs = objs.order_by('-report_date')

    objs_list = []
    for obj in objs:
        price = models.RemainderDetail.objects.filter(pharmacy_id=obj.pharmacy_id,
                                                      report_date=obj.report_date,
                                                      shift=obj.shift
                                                      ).aggregate(s=Sum('price'))['s']
        price = price if price else 0
        obj.price = price + old_obj_price
        old_obj_price = obj.price
        objs_list.append(obj)

    return models.RemainderShift.objects.bulk_update(objs_list, ['price'])
