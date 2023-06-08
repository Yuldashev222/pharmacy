from django.db.models import Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver

from api.v1.apps.incomes.models import PharmacyIncomeReportDay

from .models import Receipt


@receiver(post_delete, sender=Receipt)
def update_report(instance, *args, **kwargs):
    price = Receipt.objects.filter(report_date=instance.report_date,
                                   pharmacy_id=instance.pharmacy_id
                                   ).aggregate(s=Sum('price'))['s']

    obj, _ = PharmacyIncomeReportDay.objects.get_or_create(pharmacy_id=instance.pharmacy_id,
                                                           report_date=instance.report_date)
    obj.receipt_price = price if price else 0
    obj.save()
