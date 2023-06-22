from django.dispatch import receiver
from django.db.models import Sum
from django.db.models.signals import pre_delete

from api.v1.pharmacies.models import PharmacyReportByShift

from .models import Receipt


@receiver(pre_delete, sender=Receipt)
def update_report(instance, *args, **kwargs):
    price = Receipt.objects.exclude(id=instance.id).filter(report_date=instance.report_date,
                                                           pharmacy_id=instance.pharmacy_id
                                                           ).aggregate(s=Sum('price'))['s']

    obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=instance.pharmacy_id,
                                                         report_date=instance.report_date,
                                                         shift=instance.shift)

    obj.receipt_price = 0
    obj.save()
