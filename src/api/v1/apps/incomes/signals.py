from django.db.models import Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import PharmacyIncome, PharmacyIncomeReportDay


@receiver(post_delete, sender=PharmacyIncome)
def update_report(instance, *args, **kwargs):
    price = PharmacyIncome.objects.filter(
        report_date=instance.report_date,
        to_pharmacy_id=instance.to_pharmacy_id
    ).aggregate(s=Sum('price'))['s']
    obj = PharmacyIncomeReportDay.objects.get_or_create(
        pharmacy_id=instance.to_pharmacy_id,
        report_date=instance.report_date,
        director_id=instance.creator.director_id
    )[0]
    obj.price = price if price else 0
    print(price)
    obj.save()
