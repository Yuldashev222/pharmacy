from datetime import timedelta

from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import pre_delete

from .tasks import update_all_next_remainders
from .models import RemainderDetail, RemainderShift


@receiver(pre_delete, sender=RemainderDetail)
def update_user_income_report(instance, *args, **kwargs):
    if instance.report_date and instance.shift and instance.pharmacy:
        obj, _ = RemainderShift.objects.get_or_create(pharmacy_id=instance.pharmacy_id,
                                                      shift=instance.shift,
                                                      report_date=instance.report_date)

        if RemainderShift.objects.filter(id__lt=obj.id, pharmacy_id=obj.pharmacy_id).exists():
            report_date = obj.report_date
            if obj.shift > 1:
                shift = obj.shift - 1
            else:
                shift = 3
                report_date = obj.report_date - timedelta(days=1)

            old_obj_price = RemainderShift.get_price(obj.pharmacy_id, report_date, shift)
            price = RemainderDetail.objects.exclude(id=instance.id).filter(pharmacy_id=obj.pharmacy_id,
                                                                           report_date=obj.report_date,
                                                                           shift=obj.shift
                                                                           ).aggregate(s=Sum('price'))['s']

            obj.price = price + old_obj_price

        else:

            price = RemainderDetail.objects.exclude(id=instance.id).filter(pharmacy_id=obj.pharmacy_id,
                                                                           report_date=obj.report_date,
                                                                           shift__lte=obj.shift
                                                                           ).aggregate(s=Sum('price'))['s']
            price = price if price else 0

            price2 = RemainderDetail.objects.exclude(id=instance.id).filter(pharmacy_id=obj.pharmacy_id,
                                                                            report_date__lt=obj.report_date,
                                                                            ).aggregate(s=Sum('price'))['s']
            price += price2 if price2 else 0

            obj.price = price
        obj.save()

        update_all_next_remainders.delay(obj.pharmacy_id, str(obj.report_date), obj.shift, obj.price)
