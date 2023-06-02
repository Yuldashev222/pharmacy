from django.db.models.signals import post_save
from django.dispatch import receiver

from api.v1.apps.accounts.models import WorkerReport
from api.v1.apps.companies.enums import DefaultTransferType
from api.v1.apps.remainders.models import Remainder

from .models import DebtRepayFromPharmacy, DebtToPharmacy, DebtFromPharmacy, DebtRepayToPharmacy


@receiver(post_save, sender=DebtFromPharmacy)
def report_update(instance, *args, **kwargs):
    # remainder update
    if instance.transfer_type_id == DefaultTransferType.cash.name and not instance.is_client:
        obj, _ = Remainder.objects.get_or_create(debt_from_pharmacy_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = -1 * instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.from_pharmacy_id
        obj.save()


@receiver(post_save, sender=DebtRepayToPharmacy)
def report_update(instance, *args, **kwargs):
    # remainder update
    if instance.transfer_type_id == DefaultTransferType.cash.name:
        obj, _ = Remainder.objects.get_or_create(debt_repay_to_pharmacy_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.from_debt.from_pharmacy_id
        obj.save()


@receiver(post_save, sender=DebtRepayFromPharmacy)
def report_update(instance, *args, **kwargs):
    # remainder update
    if instance.transfer_type_id == DefaultTransferType.cash.name and not instance.from_user:
        obj, _ = Remainder.objects.get_or_create(debt_repay_from_pharmacy_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = -1 * instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.to_debt.to_pharmacy_id
        obj.save()

    # worker reports update
    if instance.from_user:
        obj, _ = WorkerReport.objects.get_or_create(debt_repay_from_pharmacy_id=instance.id)
        obj.report_date = instance.report_date
        obj.pharmacy = instance.to_debt.to_pharmacy
        obj.price = instance.price
        obj.creator_id = instance.creator_id
        obj.worker_id = instance.from_user_id
        obj.created_at = instance.created_at
        obj.save()
    else:
        WorkerReport.objects.filter(debt_repay_from_pharmacy_id=instance.id).delete()


@receiver(post_save, sender=DebtToPharmacy)
def remainder_update(instance, *args, **kwargs):
    if instance.transfer_type_id == DefaultTransferType.cash.name and not (
            instance.to_firm_expense or instance.pharmacy_expense or instance.user_expense):
        obj, _ = Remainder.objects.get_or_create(debt_to_pharmacy_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.to_pharmacy_id
        obj.save()
