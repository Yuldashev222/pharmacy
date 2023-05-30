from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from api.v1.apps.accounts.models import WorkerReport

from .models import FirmIncome, Firm, FirmExpense


@receiver(post_delete, sender=FirmIncome)
def update_firm_remaining_debts(instance, *args, **kwargs):
    not_transfer_debt = FirmIncome.objects.filter(
        is_paid=False, is_transfer_return=False, from_firm_id=instance.from_firm_id
    ).aggregate(s=Sum('remaining_debt'))['s']
    transfer_debt = FirmIncome.objects.filter(
        is_paid=False, is_transfer_return=True, from_firm_id=instance.from_firm_id
    ).aggregate(s=Sum('remaining_debt'))['s']

    obj = Firm.objects.get(id=instance.from_firm_id)
    obj.not_transfer_debt = not_transfer_debt if not_transfer_debt else 0
    obj.transfer_debt = transfer_debt if transfer_debt else 0
    obj.save()


@receiver(post_save, sender=FirmExpense)
def report_update(instance, *args, **kwargs):
    if instance.from_user:
        obj, _ = WorkerReport.objects.get_or_create(firm_expense_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = instance.price
        obj.creator_id = instance.creator_id
        obj.worker_id = instance.from_user_id
        obj.created_at = instance.created_at
        obj.save()
    else:
        WorkerReport.objects.filter(firm_expense_id=instance.id).delete()
