from django.dispatch import receiver
from django.db.models.signals import post_delete

from .models import RemainderDetail, RemainderShift


@receiver(post_delete, sender=RemainderDetail)
def update_user_income_report(instance, *args, **kwargs):
    if instance.report_date and instance.shift and instance.pharmacy:
        objs = RemainderDetail.objects.filter(pharmacy_id=instance.pharmacy_id,
                                              shift=instance.shift,
                                              report_date=instance.report_date)
        if objs.exists():
            objs.first().save()
        else:
            RemainderDetail.objects.create(pharmacy_id=instance.pharmacy_id,
                                           shift=instance.shift,
                                           report_date=instance.report_date)
