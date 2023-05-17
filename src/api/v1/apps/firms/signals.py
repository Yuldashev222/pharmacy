from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import FirmReport, FirmIncome, FirmExpense


@receiver(post_save, sender=FirmIncome)
def create_firm_income_expense_report(instance, created, *args, **kwargs):
    if created:
        FirmReport.objects.create(
            pharmacy_id=instance.to_pharmacy_id,
            firm_id=instance.from_firm_id,
            creator_id=instance.creator_id,
            report_date=instance.report_date,
            created_at=instance.created_at,
            price=instance.price,
            is_transfer=instance.is_transfer_return,
            income_id=instance.id
        )


@receiver(post_save, sender=FirmExpense)
def create_firm_income_expense_report(instance, created, *args, **kwargs):
    if created:
        FirmReport.objects.create(
            expense_id=instance.id,
            firm_worker=instance.verified_firm_worker_name,
            pharmacy_id=instance.from_pharmacy_id,
            firm_id=instance.to_firm_id,
            creator_id=instance.creator_id,
            firm_worker_phone_number=instance.verified_phone_number,
            report_date=instance.report_date,
            created_at=instance.created_at,
            price=instance.price,
            is_transfer=False if instance.transfer_type_id == 1 else True,
        )
