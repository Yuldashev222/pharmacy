from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from api.v1.apps.accounts.models import WorkerReport
from api.v1.apps.companies.enums import DefaultTransferType
from api.v1.apps.remainders.models import RemainderDetail
from api.v1.apps.pharmacies.models import PharmacyReportByShift

from .models import FirmIncome, FirmExpense, FirmReport, FirmDebtByDate


@receiver(post_delete, sender=FirmReport)
def update_firm_report(instance, *args, **kwargs):
    firm_debt, _ = FirmDebtByDate.objects.get_or_create(firm_id=instance.firm_id, report_date=instance.report_date)
    incomes_not_transfer_debt_price = FirmIncome.objects.filter(is_paid=False,
                                                                is_transfer_return=False,
                                                                from_firm_id=firm_debt.firm_id,
                                                                report_date__lte=firm_debt.report_date
                                                                ).aggregate(s=Sum('remaining_debt'))['s']
    incomes_transfer_debt_price = FirmIncome.objects.filter(is_paid=False,
                                                            is_transfer_return=True,
                                                            from_firm_id=firm_debt.firm_id,
                                                            report_date__lte=firm_debt.report_date
                                                            ).aggregate(s=Sum('remaining_debt'))['s']

    incomes_not_transfer_debt_price = incomes_not_transfer_debt_price if incomes_not_transfer_debt_price else 0
    incomes_transfer_debt_price = incomes_transfer_debt_price if incomes_transfer_debt_price else 0

    firm_debt.incomes_not_transfer_debt_price = incomes_not_transfer_debt_price
    firm_debt.incomes_transfer_debt_price = incomes_transfer_debt_price
    firm_debt.save()


@receiver(post_save, sender=FirmExpense)
def report_update(instance, *args, **kwargs):
    # remainder update
    if instance.transfer_type_id == DefaultTransferType.cash.value and not instance.from_user:
        obj, _ = RemainderDetail.objects.get_or_create(firm_expense_id=instance.id)
        obj.report_date = instance.report_date
        obj.price = -1 * instance.price
        obj.shift = instance.shift
        obj.pharmacy_id = instance.from_pharmacy_id
        obj.save()

        obj, _ = PharmacyReportByShift.objects.get_or_create(pharmacy_id=instance.from_pharmacy_id,
                                                             report_date=instance.report_date,
                                                             shift=instance.shift)
        expense_firm = FirmExpense.objects.filter(from_pharmacy_id=obj.pharmacy_id,
                                                  report_date=obj.report_date,
                                                  shift=obj.shift
                                                  ).aggregate(s=Sum('price'))['s']
        obj.expense_firm = expense_firm if expense_firm else 0
        obj.save()

    if instance.from_user:
        obj, _ = WorkerReport.objects.get_or_create(firm_expense_id=instance.id)
        obj.report_date = instance.report_date
        obj.pharmacy = instance.from_pharmacy
        obj.price = instance.price
        obj.creator_id = instance.creator_id
        obj.worker_id = instance.from_user_id
        obj.created_at = instance.created_at
        obj.save()
    else:
        WorkerReport.objects.filter(firm_expense_id=instance.id).delete()
