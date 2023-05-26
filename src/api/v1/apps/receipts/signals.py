from django.db.models import Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver

from api.v1.apps.incomes.models import PharmacyIncomeReportDay

from .models import Receipt


@receiver(post_delete, sender=Receipt)
def update_report(instance, *args, **kwargs):
    price = Receipt.objects.filter(
        report_date=instance.report_date,
        pharmacy_id=instance.pharmacy_id
    ).aggregate(s=Sum('price'))['s']
    obj = PharmacyIncomeReportDay.objects.get_or_create(
        pharmacy_id=instance.to_pharmacy_id,
        report_date=instance.report_date,
        director_id=instance.creator.director_id
    )[0]
    obj.receipt_price = price
    obj.save()
