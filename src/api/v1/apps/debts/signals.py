from django.db.models.signals import post_save
from django.dispatch import receiver

from api.v1.apps.accounts.models import WorkerReport

from .models import DebtRepayFromPharmacy


@receiver(post_save, sender=DebtRepayFromPharmacy)
def report_update(instance, *args, **kwargs):
    if instance.from_user:
        obj, _ = WorkerReport.objects.get_or_create(debt_repay_from_pharmacy_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = instance.price
        obj.creator_id = instance.creator_id
        obj.worker_id = instance.from_user_id
        obj.created_at = instance.created_at
        obj.save()
    else:
        WorkerReport.objects.filter(debt_repay_from_pharmacy_id=instance.id).delete()
