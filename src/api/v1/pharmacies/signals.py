from django.dispatch import receiver
from django.db.models.signals import pre_delete

from .models import Pharmacy
from .services import get_deleted_pharmacy_obj
from api.v1.firms.models import FirmExpense, FirmDebtByMonth, FirmReport


@receiver(pre_delete, sender=Pharmacy)
def update_connections(instance, *args, **kwargs):
    obj = get_deleted_pharmacy_obj(instance)
    FirmExpense.objects.filter(from_pharmacy_id=instance.id).update(from_pharmacy_id=obj.id)
    FirmDebtByMonth.objects.filter(pharmacy_id=instance.id).update(pharmacy_id=obj.id)
    FirmReport.objects.filter(pharmacy_id=instance.id).update(pharmacy_id=obj.id)
