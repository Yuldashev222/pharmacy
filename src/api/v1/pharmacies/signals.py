from django.dispatch import receiver
from django.db.models.signals import pre_delete

from api.v1.firms.models import FirmExpense, FirmDebtByMonth, FirmReport

from .models import Pharmacy


@receiver(pre_delete, sender=Pharmacy)
def update_connections(instance, *args, **kwargs):
    obj = Pharmacy.get_deleted_pharmacy_obj(instance.name)
    FirmReport.objects.filter(pharmacy_id=instance.id).update(pharmacy_id=obj.id)
    FirmExpense.objects.filter(from_pharmacy_id=instance.id).update(from_pharmacy_id=obj.id)
    FirmDebtByMonth.objects.filter(pharmacy_id=instance.id).update(pharmacy_id=obj.id)
