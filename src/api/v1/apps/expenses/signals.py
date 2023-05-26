from django.db.models import Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import PharmacyExpense
from .reports.models import ReturnProductReportMonth


@receiver(post_delete, sender=PharmacyExpense)
def update_report(instance, *args, **kwargs):
    price = PharmacyExpense.objects.filter(
        from_pharmacy_id=instance.from_pharmacy_id,
        report_date__year=instance.report_date.year,
        report_date__month=instance.report_date.month
    ).aggregate(s=Sum('price'))['s']
    obj = ReturnProductReportMonth.objects.get_or_create(
        pharmacy_id=instance.from_pharmacy_id,
        year=instance.report_date.year,
        month=instance.report_date.month,
        director_id=instance.from_pharmacy.director_id
    )[0]
    obj.price = price if price else 0
    print(price)
    obj.save()
