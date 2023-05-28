from django.db.models import Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import FirmIncome, Firm


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
