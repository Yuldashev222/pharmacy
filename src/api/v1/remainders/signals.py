from django.dispatch import receiver
from django.db.models import Sum
from django.db.models.signals import pre_delete

from .tasks import update_all_next_remainders
from .models import RemainderDetail, RemainderShift


@receiver(pre_delete, sender=RemainderDetail)
def update_user_income_report(instance, *args, **kwargs):
    if instance.report_date and instance.shift and instance.pharmacy:
        obj, _ = RemainderShift.objects.get_or_create(pharmacy_id=instance.pharmacy_id,
                                                      shift=instance.shift,
                                                      report_date=instance.report_date)

        obj1 = RemainderShift.objects.filter(shift__lt=obj.shift,
                                             pharmacy_id=obj.pharmacy_id,
                                             report_date=obj.report_date).order_by('-shift').first()

        obj2 = RemainderShift.objects.filter(pharmacy_id=obj.pharmacy_id,
                                             report_date__lt=obj.report_date
                                             ).order_by('-report_date', '-shift').first()

        if obj1 or obj2:
            price = RemainderDetail.objects.exclude(id=instance.id).filter(pharmacy_id=obj.pharmacy_id,
                                                                           report_date=obj.report_date,
                                                                           shift=obj.shift
                                                                           ).aggregate(s=Sum('price'))['s']
            price = price if price else 0

            if obj1:
                obj.price = price + obj1.price
            else:
                obj.price = price + obj2.price

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
