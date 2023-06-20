from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import pre_delete

from .models import RemainderDetail, RemainderShift


@receiver(pre_delete, sender=RemainderDetail)
def update_user_income_report(instance, *args, **kwargs):
    price = RemainderDetail.objects.exclude(id=instance.id).filter(pharmacy_id=instance.pharmacy_id,
                                                                   report_date=instance.report_date,
                                                                   shift__lte=instance.shift
                                                                   ).aggregate(s=Sum('price'))['s']
    price = price if price else 0
    price2 = RemainderDetail.objects.exclude(id=instance.id).filter(pharmacy_id=instance.pharmacy_id,
                                                                    report_date__lt=instance.report_date,
                                                                    ).aggregate(s=Sum('price'))['s']
    price += price2 if price2 else 0

    obj, _ = RemainderShift.objects.get_or_create(pharmacy_id=instance.pharmacy_id,
                                                  shift=instance.shift,
                                                  report_date=instance.report_date)
    obj.price = price
    obj.save()
